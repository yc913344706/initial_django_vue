import { http } from "@/utils/http";
import { apiMap } from "@/config/api";

type Result = {
  success: boolean;
  data: Array<any>;
};

export const getAsyncRoutes = () => {
  return http.request<Result>("get", apiMap.getAsyncRoutes);
};
