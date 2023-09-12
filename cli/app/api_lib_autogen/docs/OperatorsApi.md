# api_lib_autogen.OperatorsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_operator_api_v1_operators_post**](OperatorsApi.md#create_operator_api_v1_operators_post) | **POST** /api/v1/operators/ | Create Operator
[**delete_operator_api_v1_operators_id_delete**](OperatorsApi.md#delete_operator_api_v1_operators_id_delete) | **DELETE** /api/v1/operators/{id} | Delete Operator
[**read_operator_api_v1_operators_id_get**](OperatorsApi.md#read_operator_api_v1_operators_id_get) | **GET** /api/v1/operators/{id} | Read Operator
[**read_operators_api_v1_operators_get**](OperatorsApi.md#read_operators_api_v1_operators_get) | **GET** /api/v1/operators/ | Read Operators
[**update_operator_api_v1_operators_id_put**](OperatorsApi.md#update_operator_api_v1_operators_id_put) | **PUT** /api/v1/operators/{id} | Update Operator


# **create_operator_api_v1_operators_post**
> Operator create_operator_api_v1_operators_post(operator_create)

Create Operator

Create new operator.  Args:     operator_in (OperatorCreate): Parameters for new operator.  Returns:     Operator: newly created operator record

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.OperatorsApi()
operator_create = api_lib_autogen.OperatorCreate() # OperatorCreate | 

try:
    # Create Operator
    api_response = api_instance.create_operator_api_v1_operators_post(operator_create)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OperatorsApi->create_operator_api_v1_operators_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operator_create** | [**OperatorCreate**](OperatorCreate.md)|  | 

### Return type

[**Operator**](Operator.md)

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

# **delete_operator_api_v1_operators_id_delete**
> Operator delete_operator_api_v1_operators_id_delete(id)

Delete Operator

Lookup operator by id.  Args:     id (int): operator id  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: operator record that was deleted

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.OperatorsApi()
id = 56 # int | 

try:
    # Delete Operator
    api_response = api_instance.delete_operator_api_v1_operators_id_delete(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OperatorsApi->delete_operator_api_v1_operators_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Operator**](Operator.md)

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

# **read_operator_api_v1_operators_id_get**
> Operator read_operator_api_v1_operators_id_get(id)

Read Operator

Lookup operator by id.  Args:     id (int): operator id  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: operator record

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.OperatorsApi()
id = 56 # int | 

try:
    # Read Operator
    api_response = api_instance.read_operator_api_v1_operators_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OperatorsApi->read_operator_api_v1_operators_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Operator**](Operator.md)

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

# **read_operators_api_v1_operators_get**
> List[Operator] read_operators_api_v1_operators_get(skip=skip, limit=limit)

Read Operators

Retrive list of operators.  Args:     skip (int, optional): Pagination offset. Defaults to 0.     limit (int, optional): max number of records to return. Defaults to 100.  Returns:     List[Operator]: List of operators

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.OperatorsApi()
skip = 0 # int |  (optional) (default to 0)
limit = 100 # int |  (optional) (default to 100)

try:
    # Read Operators
    api_response = api_instance.read_operators_api_v1_operators_get(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OperatorsApi->read_operators_api_v1_operators_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 100]

### Return type

[**List[Operator]**](Operator.md)

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

# **update_operator_api_v1_operators_id_put**
> Operator update_operator_api_v1_operators_id_put(id, operator_update)

Update Operator

Update an existing operator.  Args:     id (int): operator id     operator_in (schemas.OperatorUpdate): operators parameters to be updated  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: updated operator record

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.OperatorsApi()
id = 56 # int | 
operator_update = api_lib_autogen.OperatorUpdate() # OperatorUpdate | 

try:
    # Update Operator
    api_response = api_instance.update_operator_api_v1_operators_id_put(id, operator_update)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OperatorsApi->update_operator_api_v1_operators_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **operator_update** | [**OperatorUpdate**](OperatorUpdate.md)|  | 

### Return type

[**Operator**](Operator.md)

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

