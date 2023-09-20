import axios, { AxiosInstance } from 'axios';

const createApiClient = (csrfToken: string, baseURL = ''): AxiosInstance => {
  const client = axios.create({
    baseURL: baseURL,
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    paramsSerializer: {
      indexes: null,
    },
  });

  client.interceptors.response.use(
    (response) => response, // Success handling, returning response unmodified
    (error) => {
      if (error.name === 'CanceledError') {
        return Promise.resolve();
      } else {
        console.error('Error:', error);
        return Promise.reject(error);
      }
    },
  );

  return client;
};

export { createApiClient };
