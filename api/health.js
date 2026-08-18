import { handleApi } from "../frontend/worker/index.js";

export default {
  fetch(request) {
    return handleApi(request, process.env, new URL(request.url));
  },
};
