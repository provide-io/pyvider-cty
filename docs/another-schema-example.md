--------------

**Implementation**:  
```python
@define
class NetworkSchemaV1:
    vpc_id = tfstr(required=True)
    subnet_id = tfstr(required=True)


@define
class NetworkSchemaV2:
    vpc_id = tfstr(required=True)
    subnet_id = tfstr(required=True)
    allowed_ips = CtyList(
        tfstr(validators=["ip_range"]),
        min_length=1
    )
```  

**Usage in Parent Schema**:  
```python
from fragments.network_v1 import NetworkSchemaV1
from fragments.network_v2 import NetworkSchemaV2

@define
class WebAppSchema:
    app_name = tfstr(required=True)
    
    # Choose fragment version dynamically
    network = tfobj(NetworkSchemaV2(), required=True)
```

------------------
