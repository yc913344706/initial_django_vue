import { defineFakeRoute } from "vite-plugin-fake-server/client";

// 模拟刷新token接口
export default defineFakeRoute([
  {
    url: "/refresh-token",
    method: "post",
    response: ({ body }) => {
      if (body.refreshToken) {
        return {
          success: true,
          data: {}
        };
      } else {
        return {
          success: false,
          data: {}
        };
      }
    }
  }
]);
