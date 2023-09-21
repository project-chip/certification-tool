// The file contents for the current environment will overwrite these during build.
// The build system defaults to the dev environment which uses `environment.ts`, but if you do
// `ng build --env=prod` then `environment.prod.ts` will be used instead.
// The list of which env maps to which file can be found in `.angular-cli.json`.

const hostName = window.location.hostname;

export const environment = {
  production: false,
  restBaseURL: 'http://' + hostName + '/api/v1/',
  webSocketBaseURL: 'ws://' + hostName + '/api/v1/ws',
  reconnectInterval: 2000,
  mockBaseURL: 'http://' + hostName + ':3000/',
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
