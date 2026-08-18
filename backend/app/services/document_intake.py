from __future__ import annotations

import csv
import html
from dataclasses import dataclass
from io import BytesIO, StringIO
from pathlib import PurePath
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

from fastapi import HTTPException, UploadFile

from app.models.schemas import ArtifactType, BackgroundArtifactExtraction, CareerProfile, UploadedArtifact


SUPPORTED_EXTENSIONS = {".txt", ".md", ".csv", ".tsv", ".json", ".docx", ".pdf", ".xlsx"}
TEXT_EXTENSIONS = {".txt", ".md", ".json"}
SPREADSHEET_EXTENSIONS = {".csv", ".tsv"}
MAX_COMBINED_TEXT_CHARS = 120_000


@dataclass(frozen=True)
class ExtractedDocument:
    filename: str
    content_type: str
    artifact_type: ArtifactType
    text: str


async def uploaded_file_to_document(file: UploadFile, max_upload_bytes: int) -> ExtractedDocument:
    filename = file.filename or "uploaded-document"
    content_type = file.content_type or "application/octet-stream"
    contents = await file.read(max_upload_bytes + 1)
    if len(contents) > max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"{filename} is too large.")

    extension = PurePath(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"{filename} is not supported. Use one of: {supported}.")

    try:
        text = extract_document_text(filename, contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail=f"{filename} did not contain readable text.")

    return ExtractedDocument(
        filename=filename,
        content_type=content_type,
        artifact_type=artifact_type_from_filename(filename),
        text=text.strip(),
    )


def extract_document_text(filename: str, contents: bytes) -> str:
    extension = PurePath(filename).suffix.lower()
    if extension in TEXT_EXTENSIONS:
        return contents.decode("utf-8", errors="replace")
    if extension in SPREADSHEET_EXTENSIONS:
        return _delimited_text(contents, delimiter="\t" if extension == ".tsv" else ",")
    if extension == ".docx":
        return _docx_text(contents, filename)
    if extension == ".xlsx":
        return _xlsx_text(contents, filename)
    if extension == ".pdf":
        return _pdf_text(contents, filename)
    raise ValueError(f"{filename} is not a supported document type.")


def artifact_type_from_filename(filename: str) -> ArtifactType:
    lowered = filename.lower()
    if "transcript" in lowered or "grade" in lowered:
        return ArtifactType.transcript
    if "portfolio" in lowered or "project" in lowered:
        return ArtifactType.portfolio
    if "certificate" in lowered or "certification" in lowered:
        return ArtifactType.certificate
    if "resume" in lowered or "cv" in lowered:
        return ArtifactType.resume
    return ArtifactType.other


def combine_documents(documents: list[ExtractedDocument]) -> UploadedArtifact:
    combined = "\n\n".join(
        f"Source document: {document.filename}\nArtifact type: {document.artifact_type.value}\n\n{document.text}"
        for document in documents
    )
    if len(combined) > MAX_COMBINED_TEXT_CHARS:
        combined = combined[:MAX_COMBINED_TEXT_CHARS]
    return UploadedArtifact(
        artifact_type=ArtifactType.other,
        filename="combined-background-documents.txt",
        content_type="text/plain",
        text=combined,
    )


def background_prompt_from_profile(extraction: BackgroundArtifactExtraction, documents: list[ExtractedDocument]) -> str:
    profile = extraction.entities
    lines = [
        "Use the background below to evaluate career fit, identify role-specific evidence, and recommend practical next steps.",
        "",
        "Candidate Background",
        _section("Education", _education_lines(profile)),
        _section("Experience", _experience_lines(profile)),
        _section("Projects", _project_lines(profile)),
        _section("Skills", profile.skills),
        _section("Certifications", profile.certifications),
        _section("Interests", profile.interests),
        _constraints_section(profile),
        "",
        "Source Documents",
        *[f"- {document.filename} ({document.artifact_type.value})" for document in documents],
    ]
    if extraction.warnings:
        lines.extend(["", "Review Notes", *[f"- {warning}" for warning in extraction.warnings]])
    return "\n".join(line for line in lines if line is not None).strip()


def _section(title: str, items: list[str]) -> str | None:
    if not items:
        return None
    return "\n".join([title, *[f"- {item}" for item in items]])


def _education_lines(profile: CareerProfile) -> list[str]:
    lines: list[str] = []
    for item in profile.education:
        parts = [item.degree, item.field, item.institution, item.dates]
        summary = ", ".join(part for part in parts if part)
        if item.highlights:
            summary = f"{summary}: {'; '.join(item.highlights)}" if summary else "; ".join(item.highlights)
        if summary:
            lines.append(summary)
    return lines


def _experience_lines(profile: CareerProfile) -> list[str]:
    lines: list[str] = []
    for item in profile.experience:
        parts = [item.title, item.organization, item.dates]
        summary = ", ".join(part for part in parts if part)
        if item.description:
            summary = f"{summary}: {item.description}" if summary else item.description
        if item.skills:
            summary = f"{summary} Skills used: {', '.join(item.skills)}" if summary else f"Skills used: {', '.join(item.skills)}"
        if summary:
            lines.append(summary)
    return lines


def _project_lines(profile: CareerProfile) -> list[str]:
    lines: list[str] = []
    for item in profile.projects:
        summary = item.name
        if item.description:
            summary = f"{summary}: {item.description}"
        if item.skills:
            summary = f"{summary} Skills used: {', '.join(item.skills)}"
        if item.url:
            summary = f"{summary} URL: {item.url}"
        lines.append(summary)
    return lines


def _constraints_section(profile: CareerProfile) -> str | None:
    constraints = profile.constraints
    values = [
        f"Location: {constraints.location}" if constraints.location else None,
        f"Timeline: {constraints.timeline}" if constraints.timeline else None,
        f"Salary: {constraints.salary}" if constraints.salary else None,
        f"Work authorization: {constraints.work_authorization}" if constraints.work_authorization else None,
        f"Weekly time budget: {constraints.time_budget_hours_per_week} hours" if constraints.time_budget_hours_per_week else None,
        *constraints.other,
    ]
    return _section("Constraints", [value for value in values if value])


def _delimited_text(contents: bytes, delimiter: str) -> str:
    decoded = contents.decode("utf-8-sig", errors="replace")
    rows = csv.reader(StringIO(decoded), delimiter=delimiter)
    return "\n".join(" | ".join(cell.strip() for cell in row if cell.strip()) for row in rows)


def _docx_text(contents: bytes, filename: str) -> str:
    try:
        with ZipFile(BytesIO(contents)) as archive:
            text_parts: list[str] = []
            for name in archive.namelist():
                if not (
                    name == "word/document.xml"
                    or name.startswith("word/header")
                    or name.startswith("word/footer")
                ):
                    continue
                text_parts.extend(_xml_text_nodes(archive.read(name)))
    except BadZipFile as exc:
        raise ValueError(f"{filename} is not a readable .docx file.") from exc
    return "\n".join(text_parts)


def _xlsx_text(contents: bytes, filename: str) -> str:
    try:
        with ZipFile(BytesIO(contents)) as archive:
            shared_strings = _xlsx_shared_strings(archive)
            text_parts: list[str] = []
            for name in sorted(archive.namelist()):
                if not name.startswith("xl/worksheets/sheet") or not name.endswith(".xml"):
                    continue
                text_parts.extend(_xlsx_sheet_rows(archive.read(name), shared_strings))
    except BadZipFile as exc:
        raise ValueError(f"{filename} is not a readable .xlsx file.") from exc
    return "\n".join(text_parts)


def _pdf_text(contents: bytes, filename: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF extraction requires pypdf. Install project dependencies, then retry the upload.") from exc

    try:
        reader = PdfReader(BytesIO(contents))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise ValueError(f"{filename} is not a readable PDF.") from exc


def _xml_text_nodes(xml_bytes: bytes) -> list[str]:
    root = ET.fromstring(xml_bytes)
    values: list[str] = []
    for element in root.iter():
        if element.tag.endswith("}t") and element.text:
            values.append(element.text)
        elif element.tag.endswith("}tab"):
            values.append("\t")
        elif element.tag.endswith("}br"):
            values.append("\n")
    return _clean_xml_text(values)


def _clean_xml_text(values: list[str]) -> list[str]:
    text = html.unescape(" ".join(values))
    lines = [line.strip() for line in text.replace("\t", " ").splitlines()]
    return [line for line in lines if line]


def _xlsx_shared_strings(archive: ZipFile) -> list[str]:
    try:
        data = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(data)
    strings: list[str] = []
    for item in root.iter():
        if not item.tag.endswith("}si"):
            continue
        values = [element.text or "" for element in item.iter() if element.tag.endswith("}t")]
        strings.append("".join(values).strip())
    return strings


def _xlsx_sheet_rows(xml_bytes: bytes, shared_strings: list[str]) -> list[str]:
    root = ET.fromstring(xml_bytes)
    rows: list[str] = []
    for row in root.iter():
        if not row.tag.endswith("}row"):
            continue
        cells: list[str] = []
        for cell in row:
            if not cell.tag.endswith("}c"):
                continue
            cell_type = cell.attrib.get("t")
            value = next((child.text for child in cell if child.tag.endswith("}v") and child.text), "")
            if cell_type == "s" and value.isdigit():
                index = int(value)
                value = shared_strings[index] if index < len(shared_strings) else ""
            if value:
                cells.append(value.strip())
        if cells:
            rows.append(" | ".join(cells))
    return rows
