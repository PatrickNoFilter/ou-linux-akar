// Serve the OU Linux static site from the Worker's assets binding.
// Routes without a matching static file return the normal 404.
export default {
  async fetch(request, env) {
    return env.ASSETS.fetch(request);
  },
};
