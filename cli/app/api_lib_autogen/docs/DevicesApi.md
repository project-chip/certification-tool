# api_lib_autogen.DevicesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_device_config_api_v1_devices_put**](DevicesApi.md#add_device_config_api_v1_devices_put) | **PUT** /api/v1/devices/ | Add Device Config
[**get_device_configs_api_v1_devices_get**](DevicesApi.md#get_device_configs_api_v1_devices_get) | **GET** /api/v1/devices/ | Get Device Configs


# **add_device_config_api_v1_devices_put**
> Any add_device_config_api_v1_devices_put(body)

Add Device Config

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.DevicesApi()
body = api_lib_autogen.Any() # Any | 

try:
    # Add Device Config
    api_response = api_instance.add_device_config_api_v1_devices_put(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DevicesApi->add_device_config_api_v1_devices_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**Any**](Any.md)

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

# **get_device_configs_api_v1_devices_get**
> Any get_device_configs_api_v1_devices_get()

Get Device Configs

### Example

```python
from __future__ import print_function
import time
import api_lib_autogen
from api_lib_autogen.rest import ApiException
from pprint import pprint

# Create an instance of the API class
api_instance = api_lib_autogen.DevicesApi()

try:
    # Get Device Configs
    api_response = api_instance.get_device_configs_api_v1_devices_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DevicesApi->get_device_configs_api_v1_devices_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Any**](Any.md)

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

