declare module '@/utils/http' {
  interface HttpResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: any;
  }

  interface HttpInstance {
    get<T = any>(url: string, config?: any): Promise<HttpResponse<T>>;
    post<T = any>(url: string, data?: any, config?: any): Promise<HttpResponse<T>>;
    put<T = any>(url: string, data?: any, config?: any): Promise<HttpResponse<T>>;
    delete<T = any>(url: string, config?: any): Promise<HttpResponse<T>>;
  }

  export const http: HttpInstance;
} 