const hostName: string = window.location.hostname;

export const environment = {
  production: true,
  restBaseURL: 'http://' + hostName + '/api/v1/',
  webSocketBaseURL: 'ws://' + hostName + '/api/v1/ws',
  reconnectInterval: 2000,
  mockBaseURL: 'http://' + hostName + '/',
  isMockActive: false
};

/**
 * Adds two numbers together.
 * @return {string} The sum of the two numbers.
 */
export function getBaseUrl() {
  if (environment.isMockActive) {
    return environment.mockBaseURL;
  } else {
    return environment.restBaseURL;
  }
}

export const toastrProps = {
  preventDuplicates: true,
  destroyByClick: true,
  duration: 10000
};

