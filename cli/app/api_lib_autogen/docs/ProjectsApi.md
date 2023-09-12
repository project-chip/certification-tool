# api_lib_autogen.ProjectsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**archive_project_api_v1_projects_id_archive_post**](ProjectsApi.md#archive_project_api_v1_projects_id_archive_post) | **POST** /api/v1/projects/{id}/archive | Archive Project
[**create_project_api_v1_projects_post**](ProjectsApi.md#create_project_api_v1_projects_post) | **POST** /api/v1/projects/ | Create Project
[**default_config_api_v1_projects_default_config_get**](ProjectsApi.md#default_config_api_v1_projects_default_config_get) | **GET** /api/v1/projects/default_config | Default Config
[**delete_project_api_v1_projects_id_delete**](ProjectsApi.md#delete_project_api_v1_projects_id_delete) | **DELETE** /api/v1/projects/{id} | Delete Project
[**read_project_api_v1_projects_id_get**](ProjectsApi.md#read_project_api_v1_projects_id_get) | **GET** /api/v1/projects/{id} | Read Project
[**read_projects_api_v1_projects_get**](ProjectsApi.md#read_projects_api_v1_projects_get) | **GET** /api/v1/projects/ | Read Projects
[**unarchive_project_api_v1_projects_id_unarchive_post**](ProjectsApi.md#unarchive_project_api_v1_projects_id_unarchive_post) | **POST** /api/v1/projects/{id}/unarchive | Unarchive Project
[**update_project_api_v1_projects_id_put**](ProjectsApi.md#update_project_api_v1_projects_id_put) | **PUT** /api/v1/projects/{id} | Update Project


# **archive_project_api_v1_projects_id_archive_post**
> Project archive_project_api_v1_projects_id_archive_post(id)

Archive Project

Archive project by id.  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was archived

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.ProjectsApi()
id = 56 # int | 

try:
    # Archive Project
    api_response = api_instance.archive_project_api_v1_projects_id_archive_post(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProjectsApi->archive_project_api_v1_projects_id_archive_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Project**](Project.md)

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

# **create_project_api_v1_projects_post**
> Project create_project_api_v1_projects_post(project_create)

Create Project

Create new project  Args:     project_in (ProjectCreate): Parameters for new project,  see schema for details  Returns:     Project: newly created project record

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.ProjectsApi()
project_create = api_lib_autogen.ProjectCreate() # ProjectCreate | 

try:
    # Create Project
    api_response = api_instance.create_project_api_v1_projects_post(project_create)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProjectsApi->create_project_api_v1_projects_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_create** | [**ProjectCreate**](ProjectCreate.md)|  | 

### Return type

[**Project**](Project.md)

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

# **default_config_api_v1_projects_default_config_get**
> TestEnvironmentConfig default_config_api_v1_projects_default_config_get()

Default Config

Return default configuration for projects.  Returns:     List[Project]: List of projects

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.ProjectsApi()

try:
    # Default Config
    api_response = api_instance.default_config_api_v1_projects_default_config_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProjectsApi->default_config_api_v1_projects_default_config_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**TestEnvironmentConfig**](TestEnvironmentConfig.md)

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

# **delete_project_api_v1_projects_id_delete**
> Project delete_project_api_v1_projects_id_delete(id)

Delete Project

Delete project by id  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was deleted

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.ProjectsApi()
id = 56 # int | 

try:
    # Delete Project
    api_response = api_instance.delete_project_api_v1_projects_id_delete(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProjectsApi->delete_project_api_v1_projects_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Project**](Project.md)

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

# **read_project_api_v1_projects_id_get**
> Project read_project_api_v1_projects_id_get(id)

Read Project

Lookup project by id  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.ProjectsApi()
id = 56 # int | 

try:
    # Read Project
    api_response = api_instance.read_project_api_v1_projects_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProjectsApi->read_project_api_v1_projects_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Project**](Project.md)

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

# **read_projects_api_v1_projects_get**
> List[Project] read_projects_api_v1_projects_get(archived=archived, skip=skip, limit=limit)

Read Projects

Retrive list of projects  Args:     archived (bool, optional): Get archived projects, when true will; get archived         projects only, when false only non-archived projects are returned.         Defaults to false.     skip (int, optional): Pagination offset. Defaults to 0.     limit (int, optional): max number of records to return. Defaults to 100.  Returns:     List[Project]: List of projects

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.ProjectsApi()
archived = False # bool |  (optional) (default to False)
skip = 0 # int |  (optional) (default to 0)
limit = 100 # int |  (optional) (default to 100)

try:
    # Read Projects
    api_response = api_instance.read_projects_api_v1_projects_get(archived=archived, skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProjectsApi->read_projects_api_v1_projects_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **archived** | **bool**|  | [optional] [default to False]
 **skip** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 100]

### Return type

[**List[Project]**](Project.md)

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

# **unarchive_project_api_v1_projects_id_unarchive_post**
> Project unarchive_project_api_v1_projects_id_unarchive_post(id)

Unarchive Project

Unarchive project by id.  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was unarchived

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.ProjectsApi()
id = 56 # int | 

try:
    # Unarchive Project
    api_response = api_instance.unarchive_project_api_v1_projects_id_unarchive_post(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProjectsApi->unarchive_project_api_v1_projects_id_unarchive_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Project**](Project.md)

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

# **update_project_api_v1_projects_id_put**
> Project update_project_api_v1_projects_id_put(id, project_update)

Update Project

Update an existing project  Args:     id (int): project id     project_in (schemas.ProjectUpdate): projects parameters to be updated  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: updated project record

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.ProjectsApi()
id = 56 # int | 
project_update = api_lib_autogen.ProjectUpdate() # ProjectUpdate | 

try:
    # Update Project
    api_response = api_instance.update_project_api_v1_projects_id_put(id, project_update)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProjectsApi->update_project_api_v1_projects_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **project_update** | [**ProjectUpdate**](ProjectUpdate.md)|  | 

### Return type

[**Project**](Project.md)

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

