# api_lib_autogen.TestRunExecutionsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**abort_testing_api_v1_test_run_executions_abort_testing_post**](TestRunExecutionsApi.md#abort_testing_api_v1_test_run_executions_abort_testing_post) | **POST** /api/v1/test_run_executions/abort-testing | Abort Testing
[**archive_api_v1_test_run_executions_id_archive_post**](TestRunExecutionsApi.md#archive_api_v1_test_run_executions_id_archive_post) | **POST** /api/v1/test_run_executions/{id}/archive | Archive
[**create_test_run_execution_api_v1_test_run_executions_post**](TestRunExecutionsApi.md#create_test_run_execution_api_v1_test_run_executions_post) | **POST** /api/v1/test_run_executions/ | Create Test Run Execution
[**download_log_api_v1_test_run_executions_id_log_get**](TestRunExecutionsApi.md#download_log_api_v1_test_run_executions_id_log_get) | **GET** /api/v1/test_run_executions/{id}/log | Download Log
[**get_test_runner_status_api_v1_test_run_executions_status_get**](TestRunExecutionsApi.md#get_test_runner_status_api_v1_test_run_executions_status_get) | **GET** /api/v1/test_run_executions/status | Get Test Runner Status
[**read_test_run_execution_api_v1_test_run_executions_id_get**](TestRunExecutionsApi.md#read_test_run_execution_api_v1_test_run_executions_id_get) | **GET** /api/v1/test_run_executions/{id} | Read Test Run Execution
[**read_test_run_executions_api_v1_test_run_executions_get**](TestRunExecutionsApi.md#read_test_run_executions_api_v1_test_run_executions_get) | **GET** /api/v1/test_run_executions/ | Read Test Run Executions
[**remove_test_run_execution_api_v1_test_run_executions_id_delete**](TestRunExecutionsApi.md#remove_test_run_execution_api_v1_test_run_executions_id_delete) | **DELETE** /api/v1/test_run_executions/{id} | Remove Test Run Execution
[**start_test_run_execution_api_v1_test_run_executions_id_start_post**](TestRunExecutionsApi.md#start_test_run_execution_api_v1_test_run_executions_id_start_post) | **POST** /api/v1/test_run_executions/{id}/start | Start Test Run Execution
[**unarchive_api_v1_test_run_executions_id_unarchive_post**](TestRunExecutionsApi.md#unarchive_api_v1_test_run_executions_id_unarchive_post) | **POST** /api/v1/test_run_executions/{id}/unarchive | Unarchive
[**upload_file_api_v1_test_run_executions_file_upload_post**](TestRunExecutionsApi.md#upload_file_api_v1_test_run_executions_file_upload_post) | **POST** /api/v1/test_run_executions/file_upload/ | Upload File


# **abort_testing_api_v1_test_run_executions_abort_testing_post**
> dict(str, str) abort_testing_api_v1_test_run_executions_abort_testing_post()

Abort Testing

Cancel the current testing

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()

try:
    # Abort Testing
    api_response = api_instance.abort_testing_api_v1_test_run_executions_abort_testing_post()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->abort_testing_api_v1_test_run_executions_abort_testing_post: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**dict(str, str)**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **archive_api_v1_test_run_executions_id_archive_post**
> TestRunExecution archive_api_v1_test_run_executions_id_archive_post(id)

Archive

Archive test run execution by id.  Args:     id (int): test run execution id  Raises:     HTTPException: if no test run execution exists for provided id  Returns:     TestRunExecution: test run execution record that was archived

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
id = 56 # int | 

try:
    # Archive
    api_response = api_instance.archive_api_v1_test_run_executions_id_archive_post(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->archive_api_v1_test_run_executions_id_archive_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestRunExecution**](TestRunExecution.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_test_run_execution_api_v1_test_run_executions_post**
> TestRunExecutionWithChildren create_test_run_execution_api_v1_test_run_executions_post(body_create_test_run_execution_api_v1_test_run_executions_post)

Create Test Run Execution

Create new test run execution.

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
body_create_test_run_execution_api_v1_test_run_executions_post = api_lib_autogen.BodyCreateTestRunExecutionApiV1TestRunExecutionsPost() # BodyCreateTestRunExecutionApiV1TestRunExecutionsPost | 

try:
    # Create Test Run Execution
    api_response = api_instance.create_test_run_execution_api_v1_test_run_executions_post(body_create_test_run_execution_api_v1_test_run_executions_post)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->create_test_run_execution_api_v1_test_run_executions_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body_create_test_run_execution_api_v1_test_run_executions_post** | [**BodyCreateTestRunExecutionApiV1TestRunExecutionsPost**](BodyCreateTestRunExecutionApiV1TestRunExecutionsPost.md)|  | 

### Return type

[**TestRunExecutionWithChildren**](TestRunExecutionWithChildren.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_log_api_v1_test_run_executions_id_log_get**
> download_log_api_v1_test_run_executions_id_log_get(id, json_entries=json_entries, download=download)

Download Log

Download the logs from a test run.   Args:     id (int): Id of the TestRunExectution the log is requested for     json_entries (bool, optional): When set, return each log line as a json object     download (bool, optional): When set, return as attachment

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
id = 56 # int | 
json_entries = False # bool |  (optional) (default to False)
download = False # bool |  (optional) (default to False)

try:
    # Download Log
    api_instance.download_log_api_v1_test_run_executions_id_log_get(id, json_entries=json_entries, download=download)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->download_log_api_v1_test_run_executions_id_log_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **json_entries** | **bool**|  | [optional] [default to False]
 **download** | **bool**|  | [optional] [default to False]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_test_runner_status_api_v1_test_run_executions_status_get**
> TestRunnerStatus get_test_runner_status_api_v1_test_run_executions_status_get()

Get Test Runner Status

Retrieve status of the Test Engine.  When the Test Engine is actively running the status will include the current test_run and the details of the states.

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()

try:
    # Get Test Runner Status
    api_response = api_instance.get_test_runner_status_api_v1_test_run_executions_status_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->get_test_runner_status_api_v1_test_run_executions_status_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**TestRunnerStatus**](TestRunnerStatus.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_test_run_execution_api_v1_test_run_executions_id_get**
> TestRunExecutionWithChildren read_test_run_execution_api_v1_test_run_executions_id_get(id)

Read Test Run Execution

Get test run by ID, including state on all children

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
id = 56 # int | 

try:
    # Read Test Run Execution
    api_response = api_instance.read_test_run_execution_api_v1_test_run_executions_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->read_test_run_execution_api_v1_test_run_executions_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestRunExecutionWithChildren**](TestRunExecutionWithChildren.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_test_run_executions_api_v1_test_run_executions_get**
> List[TestRunExecutionWithStats] read_test_run_executions_api_v1_test_run_executions_get(project_id=project_id, archived=archived, search_query=search_query, skip=skip, limit=limit)

Read Test Run Executions

Retrieve test runs, including statistics.  Args:     project_id: Filter test runs by project.     archived: Get archived test runs, when true will return archived         test runs only, when false only non-archived test runs are returned.     skip: Pagination offset.     limit: Max number of records to return.  Returns:     List of test runs with execution statistics.

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
project_id = 56 # int |  (optional)
archived = False # bool |  (optional) (default to False)
search_query = 'search_query_example' # str |  (optional)
skip = 0 # int |  (optional) (default to 0)
limit = 100 # int |  (optional) (default to 100)

try:
    # Read Test Run Executions
    api_response = api_instance.read_test_run_executions_api_v1_test_run_executions_get(project_id=project_id, archived=archived, search_query=search_query, skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->read_test_run_executions_api_v1_test_run_executions_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**|  | [optional] 
 **archived** | **bool**|  | [optional] [default to False]
 **search_query** | **str**|  | [optional] 
 **skip** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 100]

### Return type

[**List[TestRunExecutionWithStats]**](TestRunExecutionWithStats.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_test_run_execution_api_v1_test_run_executions_id_delete**
> TestRunExecutionInDBBase remove_test_run_execution_api_v1_test_run_executions_id_delete(id)

Remove Test Run Execution

Remove test run execution

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
id = 56 # int | 

try:
    # Remove Test Run Execution
    api_response = api_instance.remove_test_run_execution_api_v1_test_run_executions_id_delete(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->remove_test_run_execution_api_v1_test_run_executions_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestRunExecutionInDBBase**](TestRunExecutionInDBBase.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_test_run_execution_api_v1_test_run_executions_id_start_post**
> TestRunExecutionWithChildren start_test_run_execution_api_v1_test_run_executions_id_start_post(id)

Start Test Run Execution

Start a test run by ID

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
id = 56 # int | 

try:
    # Start Test Run Execution
    api_response = api_instance.start_test_run_execution_api_v1_test_run_executions_id_start_post(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->start_test_run_execution_api_v1_test_run_executions_id_start_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestRunExecutionWithChildren**](TestRunExecutionWithChildren.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **unarchive_api_v1_test_run_executions_id_unarchive_post**
> TestRunExecution unarchive_api_v1_test_run_executions_id_unarchive_post(id)

Unarchive

Unarchive test run execution by id.  Args:     id (int): test run execution id  Raises:     HTTPException: if no test run execution exists for provided id  Returns:     TestRunExecution: test run execution record that was unarchived

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
id = 56 # int | 

try:
    # Unarchive
    api_response = api_instance.unarchive_api_v1_test_run_executions_id_unarchive_post(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->unarchive_api_v1_test_run_executions_id_unarchive_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**TestRunExecution**](TestRunExecution.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_file_api_v1_test_run_executions_file_upload_post**
> Any upload_file_api_v1_test_run_executions_file_upload_post(file)

Upload File

Upload a file to the specified path of the current test run.  Args:     file: The file to upload.

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.TestRunExecutionsApi()
file = api_lib_autogen.IO() # IO | 

try:
    # Upload File
    api_response = api_instance.upload_file_api_v1_test_run_executions_file_upload_post(file)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TestRunExecutionsApi->upload_file_api_v1_test_run_executions_file_upload_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **IO**|  | 

### Return type

[**Any**](Any.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

