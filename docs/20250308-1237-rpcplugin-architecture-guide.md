# Pyvider RPC Plugin Architecture Guide

*Version 1.0 - March 2025*

## Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Transport System](#transport-system)
4. [Protocol Implementation](#protocol-implementation)
5. [Security Architecture](#security-architecture)
6. [Client/Server Architecture](#clientserver-architecture)
7. [Implementation Priorities](#implementation-priorities)
8. [Compatibility Strategy](#compatibility-strategy)

---

## Executive Summary

The Pyvider RPC Plugin system provides a comprehensive implementation of Terraform's plugin protocol in Python, enabling Terraform providers to be written natively in Python while maintaining full compatibility with Terraform's Go-based architecture.

This architecture:
- Implements a complete client/server model for bidirectional communication
- Supports multiple transport mechanisms (TCP and Unix sockets)
- Provides robust security through mTLS
- Handles protocol versioning and backwards compatibility
- Implements proper logging and error handling throughout
- Offers a Go-bridge for seamless integration with Terraform's plugin discovery

The design prioritizes robustness, security, and compatibility while enabling Pythonic implementation patterns through modern Python features like asyncio, attrs, and type hints.

---

## System Architecture

### Overall Design

The Pyvider RPC Plugin architecture is built around a modular, layered design that separates concerns between transport, protocol, and business logic, as shown in the previously generated system architecture diagram.

The architecture follows these core principles:
- **Separation of concerns**: Each component has a well-defined responsibility
- **Interface-based design**: Components interact through clear abstract interfaces
- **Protocol conformance**: Strictly adheres to the Terraform plugin protocol
- **Robust error handling**: Comprehensive error management throughout
- **Observability**: Detailed logging with structured emoji prefixes
- **Security-first**: Implements proper authentication and encryption

### Module Structure

The Pyvider RPC Plugin module is organized into the following key components:

```
pyvider/rpcplugin/
├── __init__.py            # Public API exports
├── exception.py           # Exception hierarchy
├── config.py              # Configuration system
├── handler.py             # RPC handler interface
├── server.py              # Server implementation
├── types.py               # Core type definitions
├── client/                # Client implementation
│   ├── __init__.py        # Client API exports
│   ├── base.py            # Base client class
│   ├── connection.py      # Client connection handling
│   └── types.py           # Client-specific types
├── crypto/                # Cryptography components
│   ├── __init__.py        # Crypto API exports
│   ├── certificate.py     # Certificate management
│   ├── constants.py       # Crypto constants
│   ├── debug.py           # Certificate debugging
│   ├── generators.py      # Key generation utilities
│   └── types.py           # Crypto-specific types
├── handshake.py           # Handshake implementation
├── logger/                # Logging system
│   ├── __init__.py        # Logger API exports
│   ├── base.py            # Logger base classes
│   ├── emoji_matrix.py    # Structured emoji logging
│   ├── formatters.py      # Log formatters
│   └── messages/          # Log message definitions
├── protocol/              # Protocol implementation
│   ├── __init__.py        # Protocol API exports
│   ├── base.py            # Protocol base class
│   ├── grpc_*.proto       # Protocol buffer definitions
│   ├── service.py         # Protocol service implementation
│   └── grpc_*_pb2*.py     # Generated protocol code
└── transport/             # Transport implementations
    ├── __init__.py        # Transport API exports
    ├── base.py            # Transport base class
    ├── tcp.py             # TCP transport implementation
    ├── types.py           # Transport-specific types
    └── unix.py            # Unix socket transport
```

### Key Components

The system is built around these core components:

1. **Transport Layer**: Provides communication channels between client and server
   - Abstract base transport interface
   - TCP socket implementation
   - Unix socket implementation
   - Transport negotiation system

2. **Protocol Layer**: Implements the gRPC-based plugin protocol
   - Protocol buffer definitions
   - Service implementations (broker, stdio, controller)
   - Handler registration system
   - Protocol negotiation

3. **Security Layer**: Manages certificates, handshake, and authentication
   - Certificate management
   - Handshake implementation
   - Magic cookie validation
   - mTLS configuration

4. **Core Services**: Configuration, logging, and exception handling
   - Hierarchical exception system
   - Environment-based configuration
   - Structured emoji logging
   - Type definitions

5. **Server/Client**: The main server and client implementations
   - Server lifecycle management
   - Client connection handling
   - Resource cleanup
   - Signal handling

### Component Interactions

The system is designed with clear interaction patterns:

- **Transport Layer** handles low-level socket communications
  - Provides a unified interface for TCP and Unix sockets
  - Manages connection establishment and termination
  - Handles data transmission
  - Implements proper cleanup

- **Protocol Layer** defines service interfaces and serialization formats
  - Leverages gRPC for service definitions
  - Implements protocol versioning
  - Provides service implementations
  - Handles message serialization/deserialization

- **Security Layer** ensures secure communications
  - Manages certificate generation and validation
  - Implements the handshake protocol
  - Configures TLS for transport security
  - Validates authentication tokens

- **Server** manages the plugin lifecycle
  - Initializes all required components
  - Handles transport selection and setup
  - Performs handshake with Terraform
  - Manages shutdown sequence

- **Client** interfaces with provider implementations
  - Provides API for provider code
  - Handles connection to the server
  - Manages service stubs
  - Implements clean shutdown

---

## Transport System

### Transport Base Class

The transport system is built on an abstract base class that defines the interface all transport implementations must follow:

```python
@attrs.define(frozen=False, slots=False)
class RPCPluginTransport(abc.ABC):
    """
    🔌🚀📝 TCP Socket Transport implementing the Transport interface.
    Provides methods to listen for connections, connect to a remote endpoint,
    and close the transport.
    """
    endpoint: str | None = attrs.field(init=False, default=None)

    @abc.abstractmethod
    async def listen(self) -> str:
        """Start listening for connections and return endpoint string."""
        pass

    @abc.abstractmethod
    async def connect(self, endpoint: str) -> None:
        """Connect to the specified endpoint."""
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the transport and clean up resources."""
        pass
```

This interface ensures that all transport implementations provide consistent behavior while allowing different underlying mechanisms.

### TCP Transport Implementation

The TCP transport implementation leverages asyncio for non-blocking operations:

```python
@attrs.define(frozen=False)
class TCPSocketTransport(RPCPluginTransport):
    """
    🔌🚀📝 TCP Socket Transport implementing the Transport interface.
    Provides methods to listen for connections, connect to a remote endpoint,
    and close the transport.
    """

    host: str = attrs.field(default="127.0.0.1")
    port: int = attrs.field(init=False, default=0)

    _server: asyncio.AbstractServer | None = attrs.field(init=False, default=None)
    _writer: asyncio.StreamWriter | None = attrs.field(init=False, default=None)
    endpoint: str | None = attrs.field(init=False, default=None)

    _transport_name: str = "tcp"

    async def listen(self) -> str:
        """
        🔌🚀🕹 Start a TCP server on a random available port and return the endpoint (host:port).
        """
        logger.debug("🔌🚀🕹: Starting listen() for TCP server...")
        try:
            self._server = await asyncio.start_server(self._handle_client, self.host, 0)
        except OSError as e:
            logger.error(f"🔌❌⚠: Failed to bind TCP server: {e}")
            raise TransportError(f"Failed to bind TCP server: {e}") from e

        try:
            sock = self._server.sockets[0]
            addr = sock.getsockname()
            self.port = addr[1]
            self.endpoint = f"{self.host}:{self.port}"
            logger.info(f"🔌✅👍: TCP server listening at {self.endpoint}")
            return self.endpoint
        except Exception as e:
            logger.error(f"🔌❌⚠: Error initializing TCP server: {e}")
            raise TransportError(f"Error initializing TCP server: {e}") from e
```

Key features of the TCP transport:

1. **Dynamic Port Allocation**: Binds to port 0 to let the OS assign an available port
2. **Asynchronous I/O**: Uses asyncio's event-driven model for efficient handling
3. **Client Handling**: Implements client connections with proper resources management
4. **Robust Error Handling**: Detailed error reporting with clear context
5. **Structured Logging**: Uses the emoji-based logging system for clarity

### Unix Socket Transport Implementation

The Unix socket transport similarly uses asyncio but works with filesystem socket paths:

```python
@attrs.define(frozen=False, slots=True)
class UnixSocketTransport(RPCPluginTransport):
    """
    Unix domain socket transport compatible with Go plugin implementation.
    """

    path: str | None = attrs.field(default=None)
    _server: asyncio.AbstractServer | None = attrs.field(init=False, default=None)
    _writer: asyncio.StreamWriter | None = attrs.field(init=False, default=None)
    _reader: asyncio.StreamReader | None = attrs.field(init=False, default=None)
    endpoint: str | None = attrs.field(init=False, default=None)

    _connections: set[ClientConnection] = attrs.field(init=False, factory=set)
    _running: bool = attrs.field(init=False, default=False)
    _closing: bool = attrs.field(init=False, default=False)
    _lock: asyncio.Lock = attrs.field(init=False, factory=asyncio.Lock)

    _transport_name: str = "unix"
```

Key features of the Unix socket transport:

1. **Socket Path Management**: Creates and manages socket files in the filesystem
2. **Stale Socket Detection**: Checks for and handles stale socket files
3. **Permission Management**: Sets appropriate permissions for cross-process access
4. **Connection Tracking**: Maintains a set of active connections for proper cleanup
5. **Concurrency Control**: Uses locks to protect shared resources

### Transport Selection and Negotiation

The system includes a transport negotiation mechanism to select the optimal transport:

```python
async def negotiate_transport(server_transports: list[str]) -> tuple[str, TransportT]:
    """
    (🗣️🚊 Transport Negotiation) Negotiates the transport type with the server and
    creates the appropriate transport instance.
    """
    logger.debug(
        f"🗣️🚊 (Transport Negotiation: Starting) => Available transports: {server_transports}"
    )
    if not server_transports:
        logger.error(
            "🗣️🚊❌ (Transport Negotiation: Failed) => No transport options provided"
        )
        raise TransportError("No transport options provided")
    try:
        # Reverse the preference - prioritize Unix sockets first
        if "unix" in server_transports:
            logger.debug(
                "🗣️🚊🧦 (Transport Negotiation: Selected Unix) => Unix socket transport is available"
            )
            transport_path = os.path.join(
                os.environ.get("TEMP_DIR", "/tmp"), f"pyvider-{os.getpid()}.sock"
            )
            from pyvider.rpcplugin.transport import UnixSocketTransport

            return "unix", UnixSocketTransport(path=transport_path)

        elif "tcp" in server_transports:
            logger.debug(
                "🗣️🚊👥 (Transport Negotiation: Selected TCP) => TCP transport is available"
            )
            from pyvider.rpcplugin.transport import TCPSocketTransport

            return "tcp", TCPSocketTransport()
        else:
            logger.error(
                "🗣️🚊❌ (Transport Negotiation: Failed) => No supported transport found",
                extra={"server_transports": server_transports},
            )
            raise TransportError(f"Unsupported transports: {server_transports}")
    except Exception as e:
        logger.error(
            "🗣️🚊❌ (Transport Negotiation: Exception) => Error during transport negotiation",
            extra={"error": str(e)},
        )
        raise TransportError(f"Error negotiating transport: {e}") from e
```

This negotiation:

1. Prioritizes Unix sockets for better performance when available
2. Falls back to TCP when Unix sockets aren't supported
3. Properly handles error cases with detailed logging
4. Creates the appropriate transport instance

The transport abstraction enables the rest of the system to work with either transport type transparently, simplifying the overall architecture.

---

## Protocol Implementation

### Protocol Base Interface

The protocol system is built around an abstract base class that defines the essential interface:

```python
class RPCPluginProtocol(ABC, Generic[ServerT, HandlerT]): 
    """
    Abstract base class for defining RPC protocols.
    ServerT: Type of gRPC server
    HandlerT: Type of handler implementation
    """

    @abstractmethod
    def get_grpc_descriptors(self) -> tuple[Any, str]:
        """Returns the protobuf descriptor set and service name."""
        pass

    @abstractmethod
    def add_to_server(self, server: ServerT, handler: HandlerT) -> None:
        """
        Adds the protocol implementation to the gRPC server.
        Args:
            server: The gRPC async server instance
            handler: The handler implementing the RPC methods
        """
        pass
```

This interface ensures that all protocol implementations provide the necessary functionality for registration with the gRPC server and descriptor retrieval.

### Protocol Services

The protocol layer implements three key services required by the Terraform plugin protocol:

1. **GRPCBroker Service**: Handles connection multiplexing for callback services
   ```python
   class GRPCBrokerService(GRPCBrokerServicer):
       """
       Implementation of the gRPC Broker logic. This matches the StartStream(...) signature in
       `grpc_broker.proto`, which transmits a stream of ConnInfo messages in both directions.
       """

       def __init__(self) -> None:
           # We hold subchannel references here.
           self._subchannels = {}

       async def StartStream(self, request_iterator, context):
           """
           StartStream is a bidirectional streaming RPC. Each side can send
           'ConnInfo' messages. We'll interpret them to open or close subchannels.
           """
           # Implementation details...
   ```

2. **GRPCController Service**: Manages plugin lifecycle
   ```python
   class GRPCControllerService(GRPCControllerServicer):
       """
       A simple Controller that can handle plugin lifecycle calls (Shutdown, Ping, etc.).
       """

       def __init__(
           self, shutdown_event: asyncio.Event, stdio_service: GRPCStdioService
       ) -> None:
           self._shutdown_event = shutdown_event
           self._stdio_service = stdio_service

       async def Shutdown(self, request, context):
           """
           In go-plugin's approach, calling 'Shutdown()' on the plugin triggers the plugin to exit.
           """
           # Implementation details...
   ```

3. **GRPCStdio Service**: Streams stdout/stderr from the plugin to Terraform
   ```python
   class GRPCStdioService(GRPCStdioServicer):
       """
       Implementation of plugin stdio streaming. Typically you want to capture
       plugin's stdout/stderr and send it back to the host.
       """

       def __init__(self) -> None:
           # We keep an internal queue for all outgoing lines.
           self._message_queue = asyncio.Queue()
           self._shutdown = False

       async def put_line(self, line: bytes, is_stderr: bool=False) -> None:
           """
           Public method: feed lines to the queue from somewhere else in your code,
           or from a logging handler that writes to the queue.
           """
           # Implementation details...

       async def StreamStdio(self, request, context):
           """
           Streams STDOUT/STDERR lines to the caller.
           """
           # Implementation details...
   ```

### Service Registration

The protocol system includes a unified registration function to attach all services to the gRPC server:

```python
def register_protocol_service(server, shutdown_event: asyncio.Event) -> None:
    """
    This function is called by your `server.py` to attach all the needed gRPC services.
    """
    # Create the "shared" Stdio service instance
    stdio_service = GRPCStdioService()

    # Initialize the broker + controller
    broker_service = GRPCBrokerService()
    controller_service = GRPCControllerService(shutdown_event, stdio_service)

    # Register them on the server
    add_GRPCStdioServicer_to_server(stdio_service, server)
    add_GRPCBrokerServicer_to_server(broker_service, server)
    add_GRPCControllerServicer_to_server(controller_service, server)

    logger.debug(
        "🔌 ProtocolService => Registered GRPCStdio, GRPCBroker, GRPCController with gRPC server."
    )
```

### Protocol Buffers

The system uses protocol buffer definitions from Terraform's plugin protocol, including:

1. **grpc_broker.proto**: Defines the connection brokering service
   ```protobuf
   message ConnInfo {
       uint32 service_id = 1;
       string network = 2;
       string address = 3;
       message Knock {
           bool knock = 1;
           bool ack = 2;
           string error = 3;
       }
       Knock knock = 4;
   }

   service GRPCBroker {
       rpc StartStream(stream ConnInfo) returns (stream ConnInfo);
   }
   ```

2. **grpc_controller.proto**: Defines the controller service
   ```protobuf
   message Empty {
   }

   service GRPCController {
       rpc Shutdown(Empty) returns (Empty);
   }
   ```

3. **grpc_stdio.proto**: Defines the stdio streaming service
   ```protobuf
   service GRPCStdio {
     rpc StreamStdio(google.protobuf.Empty) returns (stream StdioData);
   }

   message StdioData {
     enum Channel {
       INVALID = 0;
       STDOUT = 1;
       STDERR = 2;
     }

     Channel channel = 1;
     bytes data = 2;
   }
   ```

These definitions are compiled to Python code using the protobuf compiler, generating the necessary gRPC client and server code.

### Protocol Versioning

The system supports multiple protocol versions with negotiation:

```python
def negotiate_protocol_version(server_versions: list[int]) -> int:
    """
    🤝🔄 Selects the highest mutually supported protocol version.
    """
    logger.debug(
        f"🤝🔄 Negotiating protocol version. Server supports: {server_versions}"
    )
    SUPPORTED_PROTOCOL_VERSIONS = rpcplugin_config.get("SUPPORTED_PROTOCOL_VERSIONS")
    for version in sorted(server_versions, reverse=True):
        if version in SUPPORTED_PROTOCOL_VERSIONS:
            logger.info(f"🤝✅ Selected protocol version: {version}")
            return version

    logger.error(
        f"🤝❌ Protocol negotiation failed: No compatible version found. "
        f"Server supports: {server_versions}, Client supports: {SUPPORTED_PROTOCOL_VERSIONS}"
    )
    raise ProtocolError(
        f"No mutually supported protocol version found. Server supports: {server_versions}, "
        f"Client supports: {SUPPORTED_PROTOCOL_VERSIONS}"
    )
```

This negotiation ensures compatibility between different versions of Terraform and the plugin.

---

## Security Architecture

### Certificate System

The certificate system provides comprehensive management of X.509 certificates for mTLS:

```python
@attrs.define(slots=True, frozen=True)
class CertificateBase:
    """Immutable base certificate data."""

    subject: x509.Name
    issuer: x509.Name
    public_key: PublicKey
    not_valid_before: datetime
    not_valid_after: datetime
    serial_number: int

    @classmethod
    def create(cls, config: CertificateConfig) -> tuple[Self, KeyPair]:
        """
        📜📝🚀 CertificateBase.create: Create a new certificate base and private key.
        """
        # Implementation details...
```

The certificate system includes:

1. **Certificate Generation**: Creates self-signed certificates for mTLS
   ```python
   def _create_x509_certificate(self) -> x509.Certificate:
       """
       📜📝🚀 _create_x509_certificate: Builds and signs an X.509 certificate.
       """
       # Implementation details...
   ```

2. **Certificate Validation**: Verifies certificate trust chains
   ```python
   def verify_trust(self, other_cert: "Certificate") -> bool:
       """
       📜🔍🚀 verify_trust: Verifies that the other certificate is trusted.
       """
       # Implementation details...
   ```

3. **Certificate Debugging**: Tools for certificate inspection
   ```python
   def display_cert_details(self) -> None:
       """
       📜📂🚀 display_cert_details: Logs detailed certificate information.
       """
       # Implementation details...
   ```

4. **Key Management**: Supports different key types and parameters
   ```python
   def generate_keypair(
       key_type: str = KEY_TYPE_ECDSA, key_size: int = 2048, curve_name: str = "secp521r1"
   ) -> KeyPairType:
       """
       Generates an RSA or ECDSA keypair based on the given parameters.
       """
       # Implementation details...
   ```

### Handshake Process

The handshake process is the core of the security architecture, ensuring secure establishment of communications:

```python
async def build_handshake_response(
    plugin_version: int,
    transport_name: str,
    transport: TransportT,
    server_cert: Certificate | None = None,
    port: int | None = None,
) -> str:
    """
    🤝📝✅ Constructs the handshake response string in the format:
    CORE_VERSION|PLUGIN_VERSION|NETWORK|ADDRESS|PROTOCOL|TLS_CERT
    """
    logger.debug("🤝📝🔄 Building handshake response...")

    try:
        if transport_name == "tcp":
            if port is None:
                logger.error("🤝📝❌ TCP transport requires a valid port.")
                raise ValueError("TCP transport requires a valid port.")
            endpoint = f"127.0.0.1:{port}"
            logger.debug(f"🤝📝✅ TCP endpoint set: {endpoint}")

        elif transport_name == "unix":
            if hasattr(transport, '_running') and transport._running and transport.endpoint:
                logger.debug(f"🤝📝✅ Using existing Unix transport endpoint: {transport.endpoint}")
                endpoint = transport.endpoint
            else:
                logger.debug("🤝📝🔄 Waiting for Unix transport to listen...")
                endpoint = await transport.listen()
                logger.debug(f"🤝📝✅ Unix transport endpoint received: {endpoint}")
        else:
            logger.error(f"🤝📝❌ Unsupported transport type: {transport_name}")
            raise TransportError(f"Unsupported transport: {transport_name}")

        # Rest of implementation...
    except Exception as e:
        logger.error(
            f"🤝📝❌ Handshake response build failed: {e}", extra={"error": str(e)}
        )
        raise
```

The handshake process includes:

1. **Magic Cookie Validation**: Ensures both sides have the correct authentication token
   ```python
   def validate_magic_cookie(
       magic_cookie_key: str | None = _SENTINEL,
       magic_cookie_value: str | None = _SENTINEL,
       magic_cookie: str | None = _SENTINEL,
   ) -> None:
       """
       🍪🔍 Validates the magic cookie.
       """
       # Implementation details...
   ```

2. **Protocol Negotiation**: Selects a compatible protocol version
   ```python
   def negotiate_protocol_version(server_versions: list[int]) -> int:
       """
       🤝🔄 Selects the highest mutually supported protocol version.
       """
       # Implementation details...
   ```

3. **Transport Type Validation**: Ensures the transport type is supported
   ```python
   def validate_transport(transport_name: str, supported_transports: list[str]) -> None:
       """
       🚂🔍 Validates whether the specified transport is supported.
       """
       # Implementation details...
   ```

4. **Certificate Exchange**: Optionally includes server certificate for mTLS
   ```python
   # In build_handshake_response:
   if server_cert:
       logger.debug("🤝🔐🔄 Processing server certificate...")
       cert_lines = server_cert.cert.strip().split("\n")
       if len(cert_lines) < 3:
           logger.error("🤝🔐❌ Invalid certificate format.")
           raise ValueError("Invalid certificate format")
       # Remove header and footer, then remove trailing '=' characters.
       cert_body = "".join(cert_lines[1:-1]).rstrip("=")
       response_parts[-1] = cert_body
       logger.debug("🤝🔐✅ Certificate data added to response.")
   ```

### TLS Channel Security

The system implements secure gRPC channels with TLS:

```python
def _generate_server_credentials(
    self, client_cert: str | None
) -> grpc.ServerCredentials | None:
    """
    Generates gRPC server TLS credentials using the Certificate API.
    """
    logger.debug("🛎️ Generating server credentials using Certificate API.")
    try:
        if not client_cert:
            logger.debug("🛎️ Insecure mode: skipping TLS setup.")
            return None

        server_cert_conf = rpcplugin_config.get("PLUGIN_SERVER_CERT")
        server_key_conf = rpcplugin_config.get("PLUGIN_SERVER_KEY")
        self._server_cert_obj = Certificate(
            cert=server_cert_conf,
            key=server_key_conf,
            generate_keypair=not (server_cert_conf and server_key_conf),
            key_type="ecdsa",
            common_name="localhost",
        )
        logger.debug("🛎️ Server certificate loaded/generated successfully.")

        key_bytes = self._server_cert_obj.key.encode() if isinstance(self._server_cert_obj.key, str) else self._server_cert_obj.key
        cert_bytes = self._server_cert_obj.cert.encode() if isinstance(self._server_cert_obj.cert, str) else self._server_cert_obj.cert
        client_cert_bytes = client_cert.encode() if isinstance(client_cert, str) else client_cert

        creds = grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[(key_bytes, cert_bytes)],
            root_certificates=client_cert_bytes,
            require_client_auth=False,
        )
        logger.debug("🛎️ Server TLS credentials created with mTLS enabled.")
        return creds
    except Exception as e:
        logger.error(
            "🛎️❌ Error generating server credentials", extra={"error": str(e)}
        )
        raise
```

This implementation ensures:

1. **Secure Communication**: All data is encrypted in transit
2. **Certificate-Based Authentication**: Verifies the identity of both client and server
3. **Configurable Security**: Supports both secure and insecure modes
4. **Proper Certificate Handling**: Manages certificate loading and generation

---

## Client/Server Architecture

### Server Implementation

The server component manages the complete lifecycle of a plugin instance:

```python
@attrs.define(slots=False)
class RPCPluginServer(ABC, Generic[ServerT, HandlerT, TransportT, ProtocolT]):
    """
    RPCPluginServer initializes and runs a gRPC server according to negotiated
    handshake parameters. It supports mTLS via the Certificate API and can use
    either TCP or Unix socket transports.
    """

    # Public initialization parameters.
    protocol: ProtocolT = attrs.field()
    handler: HandlerT = attrs.field()
    config: ClientT | None = attrs.field(default=None)
    transport: TransportT | None = attrs.field(default=None)

    _exit_on_stop: bool = attrs.field(default=True, init=False)

    # Internal attributes.
    _transport: TransportT | None = attrs.field(init=False, default=None)
    _server: ServerT | None = attrs.field(init=False, default=None)
    _handshake_config: HandshakeConfig = attrs.field(init=False)
    _protocol_version: int = attrs.field(init=False)
    _transport_name: str = attrs.field(init=False)
    _server_cert_obj: Certificate | None = attrs.field(init=False, default=None)
    _port: int | None = attrs.field(init=False, default=None)
    _serving_future: asyncio.Future = attrs.field(init=False, factory=asyncio.Future)
    _serving_event: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)
    _shutdown_event: asyncio.Event = attrs.field(init=False, factory=asyncio.Event)

    # Class-level instance for global access.
    _instance: ServerT | None = None
    
    # Rest of implementation...
```

Key aspects of the server implementation:

1. **Lifecycle Management**: Controls the server startup, operation, and shutdown
   ```python
   async def serve(self) -> None:
       logger.debug("🛎️ Entering serve(); starting server setup...")
       try:
           self._register_signal_handlers()
           await self._negotiate_handshake()
           client_cert = self._read_client_cert()
           await self._setup_server(client_cert)
       except Exception as e:
           logger.error(
               "🛎️❌ Serve() failed during setup",
               extra={"error": str(e), "trace": traceback.format_exc()},
           )
           raise

       # Rest of implementation...
   ```

2. **Signal Handling**: Manages OS signals for graceful termination
   ```python
   def _register_signal_handlers(self) -> None:
       logger.debug("🛎️ Registering signal handlers for graceful shutdown...")
       try:
           loop = asyncio.get_event_loop()
           for sig in (signal.SIGINT, signal.SIGTERM):
               try:
                   loop.add_signal_handler(sig, self._shutdown_requested)
                   logger.debug(f"🛎️ Signal handler registered for {sig.name}.")
               except NotImplementedError:
                   logger.warning(
                       f"🛎️ Signal handler for {sig.name} not supported on this platform."
                   )
       except Exception as e:
           logger.exception(
               "Error registering signal handlers",
               extra={"error": str(e), "trace": traceback.format_exc()},
           )
   ```

3. **Transport Management**: Sets up the appropriate transport
   ```python
   async def _negotiate_handshake(self) -> bool | None:
       logger.debug("🤝 Starting handshake negotiation...")
       try:
           validate_magic_cookie()

           logger.debug("🤝 Magic cookie validated.")
           self._protocol_version = negotiate_protocol_version(
               self._handshake_config.protocol_versions
           )
           logger.info(f"🤝 Selected protocol version: {self._protocol_version}")

           if self.transport:
               # Handle transport setup...
           else:
               logger.debug("🤝 Negotiating transport from configuration...")
               supported_transports = self._handshake_config.supported_transports
               if callable(supported_transports):
                   supported_transports = supported_transports()
               self._transport_name, self._transport = await negotiate_transport(
                   supported_transports
               )
           logger.debug(
               f"🤝 Handshake negotiation completed; transport selected: {self._transport_name}."
           )

           return True
       except Exception as e:
           logger.error(
               "🤝❌ Handshake negotiation failed",
               extra={"error": str(e), "trace": traceback.format_exc()},
           )
           raise HandshakeError(f"Handshake negotiation failed: {e}") from e
   ```

4. **Server Configuration**: Sets up the gRPC server
   ```python
   async def _setup_server(self, client_cert: str | None) -> None:
       """
       Sets up the gRPC server instance and registers the provider service.
       """
       logger.debug("🛎️ Setting up gRPC server instance...")
       try:
           self._server = GRPCServer(
               options=[
                   ("grpc.ssl_target_name_override", "localhost"),
                   ("grpc.use_local_subchannel_pool", 1),
                   ("grpc.max_receive_message_length", 16 * 1024 * 1024),
                   ("grpc.max_send_message_length", 16 * 1024 * 1024),
                   ("grpc.keepalive_time_ms", 10000),
                   ("grpc.keepalive_timeout_ms", 5000),
                   ("grpc.keepalive_permit_without_calls", True),
                   ("grpc.http2.max_pings_without_data", 0),
                   ("grpc.http2.min_time_between_pings_ms", 10000),
                   ("grpc.http2.min_ping_interval_without_data_ms", 5000),
               ]
           )
           logger.debug("🛎️ gRPC server instance created.")
       except Exception as e:
           logger.error(
               "🛎️❌ gRPC server setup failed",
               extra={"error": str(e), "trace": traceback.format_exc()},
           )
           raise

       # Rest of implementation...
   ```

5. **Clean Shutdown**: Ensures proper resource cleanup
   ```python
   async def stop(self) -> None:
       logger.debug("🛎️ Stopping server...")

       # Cancel any pending tasks first
       all_tasks = [task for task in asyncio.all_tasks()
                   if task is not asyncio.current_task() and
                      not task.done() and
                      task.get_name().startswith('RPCPlugin')]

       for task in all_tasks:
           task.cancel()

       try:
           await asyncio.wait_for(asyncio.gather(*all_tasks, return_exceptions=True), timeout=2.0)
       except asyncio.TimeoutError:
           logger.warning("🛎️ Timed out waiting for tasks to cancel")

       # Stop gRPC server with timeout
       if self._server:
           try:
               await asyncio.wait_for(self._server.stop(grace=1.0), timeout=2.0)
               logger.debug("🛎️ gRPC server stopped successfully.")
           except Exception as e:
               logger.error(f"🛎️❌ Error stopping gRPC server: {e}")
           finally:
               self._server = None

       # Close transport with timeout
       if self._transport:
           try:
               await asyncio.wait_for(self._transport.close(), timeout=3.0)
               logger.debug("🛎️ Transport closed successfully.")
           except Exception as e:
               logger.error(f"🛎️❌ Error closing transport: {e}")
           finally:
               self._transport = None

       # Ensure serving future completion
       if hasattr(self, '_serving_future') and self._serving_future and not self._serving_future.done():
           self._shutdown_requested()

       logger.debug("🛎️ Server shutdown complete.")
   ```

### Client Implementation

The client component provides the API for provider implementations:

```python
@attrs.define
class RPCPluginClient:
    """
    RPCPluginClient updated to interact with the new broker, stdio, and controller services.
    This version:
      • Launches or attaches to a plugin server subprocess.
      • Performs handshake, sets up TLS.
      • Creates a secure gRPC channel.
      • Exposes methods to:
         => read plugin logs (StdioStub.StreamStdio)
         => manage broker subchannels (BrokerStub.StartStream)
         => send shutdown signals (ControllerStub.Shutdown).
    """

    command: list[str] = attrs.field()
    config: dict[str, Any] | None = attrs.field(default=None)

    # Internal fields
    _process: subprocess.Popen | None = attrs.field(init=False, default=None)
    _transport: TransportT | None = attrs.field(init=False, default=None)
    _address: TransportT | None = attrs.field(init=False, default=None)
    _protocol_version: int | None = attrs.field(init=False, default=None)
    _server_cert: str | None = attrs.field(init=False, default=None)
    _channel: grpc.aio.Channel | None = attrs.field(init=False, default=None)

    # Generated or loaded client certificate
    client_cert: str | None = attrs.field(init=False, default=None)
    client_key_pem: str | None = attrs.field(init=False, default=None)

    # gRPC stubs for the new services
    _stdio_stub: GRPCStdioStub | None = attrs.field(init=False, default=None)
    _broker_stub: GRPCBrokerStub | None = attrs.field(init=False, default=None)
    _controller_stub: GRPCControllerStub | None = attrs.field(init=False, default=None)

    # Tasks for asynchronous streaming (e.g., reading stdio or broker streams)
    _stdio_task: asyncio.Task | None = attrs.field(init=False, default=None)
    _broker_task: asyncio.Task | None = attrs.field(init=False, default=None)
    
    # Rest of implementation...
```

Key aspects of the client implementation:

1. **Certificate Setup**: Configures TLS certificates
   ```python
   async def _setup_client_certificates(self) -> None:
       """
       If PLUGIN_AUTO_MTLS is true, load or generate a client certificate and key.
       """
       logger.debug("🔐 Checking if auto-mTLS is enabled for client.")
       auto_mtls = rpcplugin_config.get("PLUGIN_AUTO_MTLS", "").lower()
       if auto_mtls in ("true", "1", "yes"):
           cert_pem = rpcplugin_config.get("PLUGIN_CLIENT_CERT", "")
           key_pem = rpcplugin_config.get("PLUGIN_CLIENT_KEY", "")
           if cert_pem and key_pem:
               logger.info("🔐 Using existing client cert/key from config.")
               self.client_cert = cert_pem
               self.client_key_pem = key_pem
           else:
               logger.info("🔐 Generating ephemeral self-signed client certificate.")
               client_cert_obj = Certificate(generate_keypair=True, key_type="ecdsa")
               self.client_cert = client_cert_obj.cert
               self.client_key_pem = client_cert_obj.key
       else:
           logger.info("🔐 mTLS not enabled; operating in insecure mode.")
   ```

2. **Process Management**: Launches and manages the server subprocess
   ```python
   async def _launch_process(self) -> None:
       """Launch the plugin as a subprocess if not already running."""
       if self._process:
           logger.debug("🖥️ Plugin subprocess is already running; skipping launch.")
           return

       env = os.environ.copy()
       if self.config and "env" in self.config:
           env.update(self.config["env"])

       # Force unbuffered output in Python subprocesses
       env["PYTHONUNBUFFERED"] = "1"

       # Configure Go process environment for better interoperability
       # These settings help Go's stdout flushing behavior
       env["GODEBUG"] = env.get("GODEBUG", "") + ",asyncpreemptoff=1"
       env["GOOPTS"] = env.get("GOOPTS", "") + " -gcflags=all=-N"  # Disable optimizations

       # Pass client cert if needed
       if self.client_cert:
           env["PLUGIN_CLIENT_CERT"] = self.client_cert

       logger.debug(f"🖥️ Launching plugin subprocess with command: {self.command}")
       try:
           self._process = subprocess.Popen(
               self.command,
               env=env,
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE,
               text=False,
               bufsize=0,  # Disable buffering
               universal_newlines=False,
           )
           logger.info("🖥️ Plugin subprocess started successfully.")
       except Exception as e:
           logger.error(f"🖥️❌ Failed to launch plugin subprocess: {e}",
                       extra={"trace": traceback.format_exc()})
           raise
   ```

3. **Handshake Execution**: Performs handshake with the server
   ```python
   async def _perform_handshake(self) -> None:
       """
       Reads a single line from the plugin stdout for handshake:
         => Format: CORE_VERSION|PLUGIN_VERSION|network|address|protocol|serverCert
       """
       logger.debug("🤝 Initiating handshake with plugin server...")

       if not self._process or not self._process.stdout:
           raise HandshakeError("No server process or no stdout available.")

       # Start stderr relay immediately to see any error output
       await self._relay_stderr_background()

       # Log the command being used
       logger.debug(f"🤝 Waiting for handshake from command: {self.command}")

       # Read handshake line implementation...
       
       # Parse handshake
       try:
           core_version, protocol_version, network, address, protocol, server_cert = (
               parse_handshake_response(line)
           )
           logger.debug(
               f"🤝 Handshake parse => core_version={core_version}, "
               f"protocol_version={protocol_version}, network={network}, "
               f"address={address}, protocol={protocol}, cert={bool(server_cert)}"
           )
           self._protocol_version = protocol_version
           self._server_cert = server_cert

           if network == "tcp":
               self._transport = TCPSocketTransport()
               logger.debug("*** network is set to tcp")
           elif network == "unix":
               # More robust handling of unix: prefix formats
               logger.debug("*** network is set to unix")

               if address.startswith("unix:"):
                   logger.debug("*** address starts with unix")
                   self._address = address[5:]  # Remove standard unix: prefix
                   # Remove leading slashes (but not all slashes)
                   while self._address.startswith("/") and not self._address.startswith("//"):
                       self._address = self._address[1:]

               else:
                   self._address = address

               logger.debug(f"🤝🔍 Normalized Unix path from '{address}' to '{self._address}'")
               self._transport = UnixSocketTransport(path=self._address)
           else:
               raise TransportError(f"Unsupported transport: {network}")

           # Connect the chosen transport
           await self._transport.connect(address)
           logger.info(f"🚄 Transport connected via {network} -> {address}")
       except Exception as e:
           logger.error(
               "🤝❌ Error parsing handshake response or connecting transport.",
               extra={"trace": traceback.format_exc()},
           )
           raise HandshakeError(f"Handshake parse/connect error: {e}") from e
   ```

4. **Channel Creation**: Sets up the gRPC channel
   ```python
   async def _create_grpc_channel(self) -> None:
       """Creates a secure gRPC channel to the plugin."""
       logger.debug("🚢 Attempting to create gRPC channel to plugin...")

       # CRITICAL FIX: Use the same address that was established during handshake
       if isinstance(self._transport, UnixSocketTransport):
           # For Unix sockets, we must use the exact same socket path from handshake
           target = f"unix:{self._address}"
       else:
           # For TCP, use standard addressing
           target = f"{self._network}:{self._address}"

       logger.debug(f"🚢🔍 Creating gRPC channel with target: {target}")

       # Rebuild server cert into PEM if needed
       if self._server_cert:
           full_pem = self._rebuild_x509_pem(self._server_cert)

           # Set up credentials
           if self.client_cert and self.client_key_pem:
               logger.debug("🔐 Creating mTLS channel with client certs + server root.")
               credentials = grpc.ssl_channel_credentials(
                   root_certificates=full_pem.encode(),
                   private_key=self.client_key_pem.encode(),
                   certificate_chain=self.client_cert.encode()
               )
           else:
               logger.debug("🔐 Creating TLS channel with server cert only.")
               credentials = grpc.ssl_channel_credentials(
                   root_certificates=full_pem.encode()
               )

           # Create the secure channel
           self._channel = grpc.aio.secure_channel(
               target,
               credentials,
               options=[
                   ("grpc.ssl_target_name_override", "localhost"),
                   ("grpc.max_receive_message_length", 32 * 1024 * 1024),
                   ("grpc.max_send_message_length", 32 * 1024 * 1024),
                   ("grpc.keepalive_time_ms", 10000),
                   ("grpc.keepalive_timeout_ms", 5000)
               ]
           )
       else:
           # Fall back to insecure channel if no cert
           logger.info("🚢 No server certificate. Using insecure channel.")
           self._channel = grpc.aio.insecure_channel(target)

       logger.debug("🚢 gRPC channel created successfully.")

       # Wait for the channel to be ready with timeout
       try:
           await asyncio.wait_for(self._channel.channel_ready(), timeout=5.0)
           logger.debug("🚢✅ gRPC channel ready and connected.")
       except asyncio.TimeoutError:
           socket_path = target.replace("unix:", "") if target.startswith("unix:") else None
           logger.error(f"🚢❌ gRPC channel failed to become ready (timeout)")
           if socket_path:
               logger.error(f"🚢❌ Socket diagnostics: path={socket_path}, exists={os.path.exists(socket_path)}")
           raise ConnectionError("Failed to establish gRPC channel to plugin: timeout")
       except Exception as e:
           logger.error(f"🚢❌ gRPC channel failed: {e}")
           raise ConnectionError(f"Failed to establish gRPC channel to plugin: {e}")
   ```

5. **Stub Initialization**: Creates gRPC service stubs
   ```python
   def _init_stubs(self) -> None:
       """
       Once the channel is established, create stubs for Stdio, Broker, and Controller.
       """
       if not self._channel:
           raise RuntimeError("Cannot init stubs; no gRPC channel available.")

       logger.debug(
           "🔌 Creating GRPCStdioStub, GRPCBrokerStub, GRPCControllerStub from channel."
       )
       self._stdio_stub = GRPCStdioStub(self._channel)
       self._broker_stub = GRPCBrokerStub(self._channel)
       self._controller_stub = GRPCControllerStub(self._channel)
   ```

6. **Service Interaction**: Methods for using the gRPC services
   ```python
   async def _read_stdio_logs(self) -> None:
       """
       Subscribes to the plugin's stdio stream. This is an infinite loop
       that reads messages from the plugin, logs them, and prints them.
       """
       if not self._stdio_stub:
           logger.debug("🔌📝 _read_stdio_logs called, but no _stdio_stub. Exiting.")
           return
       logger.debug("🔌📝 Starting to read plugin's stdio stream...")

       try:
           # We call StreamStdio once. The plugin sends us lines until it shuts down.
           async for chunk in self._stdio_stub.StreamStdio(empty_pb2.Empty()):
               if chunk.channel == StdioData.STDERR:
                   logger.debug(f"🔌📝📥 Plugin STDERR: {chunk.data!r}")
               else:
                   logger.debug(f"🔌📝📥 Plugin STDOUT: {chunk.data!r}")
       except asyncio.CancelledError:
           logger.debug(
               "🔌📝 read_stdio_logs task cancelled. Shutting down stdio read."
           )
       except Exception as e:
           logger.error(
               f"🔌📝❌ Error reading plugin stdio stream: {e}",
               extra={"trace": traceback.format_exc()},
           )

       logger.debug("🔌📝 Plugin stdio reading loop ended.")
   ```

7. **Cleanup**: Ensures proper resource management
   ```python
   async def close(self) -> None:
       """
       Gracefully shut down the client:
        • Cancel tasks (e.g. reading stdio logs).
        • Close gRPC channel.
        • Terminate the plugin subprocess.
        • Close transport sockets.
       """
       logger.debug("🔄 Closing RPCPluginClient...")

       # Cancel reading tasks
       tasks_to_cancel = []
       if self._stdio_task and not self._stdio_task.done():
           tasks_to_cancel.append(self._stdio_task)
       if self._broker_task and not self._broker_task.done():
           tasks_to_cancel.append(self._broker_task)

       for t in tasks_to_cancel:
           t.cancel()
           with contextlib.suppress(asyncio.CancelledError):
               await t

       # Close gRPC channel
       if self._channel:
           logger.debug("🔄 Closing gRPC channel...")
           await self._channel.close()
           logger.debug("🔄 gRPC channel closed.")
           self._channel = None

       # Terminate plugin process
       if self._process:
           logger.debug("🔄 Terminating plugin subprocess...")
           try:
               self._process.terminate()
               self._process.wait(timeout=7) # should be higher than the server timeout
               logger.debug("🔄 Plugin subprocess terminated.")
           except Exception as e:
               logger.error(
                   f"🔄❌ Error terminating plugin process: {e}",
                   extra={"trace": traceback.format_exc()},
               )
           self._process = None

       # Close underlying transport
       if self._transport:
           logger.debug("🔄 Closing transport socket...")
           await self._transport.close()
           logger.debug("🔄 Transport socket closed.")
           self._transport = None

       logger.info("🔄 RPCPluginClient fully closed.")
   ```

### Connection Management

Client connections are managed using a dedicated class:

```python
@attrs.define(slots=True, frozen=False)
class ClientConnection:
    """
    Represents an active client connection with associated metrics and state.

    This class wraps the asyncio StreamReader and StreamWriter with additional
    functionality for tracking metrics and managing connection state. It now
    supports dependency injection for its I/O functions, allowing tests or
    alternative implementations to override the default behavior.

    Attributes:
        reader: Stream for reading client data.
        writer: Stream for writing responses.
        remote_addr: Remote address of the client.
        bytes_sent: Total bytes sent over this connection.
        bytes_received: Total bytes received over this connection.
        send_func: Callable used to send data; defaults to _default_send.
        receive_func: Callable used to receive data; defaults to _default_receive.
    """

    reader: asyncio.StreamReader = attrs.field()
    writer: asyncio.StreamWriter = attrs.field()
    remote_addr: str = attrs.field()
    bytes_sent: int = attrs.field(default=0)
    bytes_received: int = attrs.field(default=0)
    _closed: bool = attrs.field(default=False, init=False)
    send_func: SendFuncType | None = attrs.field(default=None)
    receive_func: ReceiveFuncType | None = attrs.field(default=None)
    
    # Rest of implementation...
```

This connection class:

1. **Tracks Metrics**: Monitors data sent and received
   ```python
   def update_metrics(self, bytes_sent: int = 0, bytes_received: int = 0) -> None:
       """
       Update connection metrics.

       Args:
           bytes_sent: Number of bytes sent.
           bytes_received: Number of bytes received.
       """
       self.bytes_sent += bytes_sent
       self.bytes_received += bytes_received
       logger.debug(
           f"Updated metrics for {self.remote_addr}",
           extra={
               "total_sent": self.bytes_sent,
               "total_received": self.bytes_received,
           },
       )
   ```

2. **Manages I/O**: Handles data transmission with error handling
   ```python
   async def _default_send(self, data: bytes) -> None:
       """
       Default send function: writes data to the writer and updates metrics.
       """
       try:
           self.writer.write(data)
           await self.writer.drain()
           self.update_metrics(bytes_sent=len(data))
           logger.debug(f"Sent data to {self.remote_addr}", extra={"bytes": len(data)})
       except OSError as e:
           logger.error(
               f"Error sending data to {self.remote_addr}", extra={"error": str(e)}
           )
           raise
   ```

3. **Ensures Cleanup**: Properly closes resources
   ```python
   async def close(self) -> None:
       """
       Close the connection and clean up resources.

       This method is idempotent and can be safely called multiple times.
       """
       if self._closed:
           return

       logger.debug(f"Closing connection to {self.remote_addr}")
       self._closed = True

       if not self.writer.is_closing():
           try:
               self.writer.close()
               await self.writer.wait_closed()
               logger.debug(f"Connection to {self.remote_addr} closed successfully")
           except Exception as e:
               logger.error(
                   f"Error while closing connection to {self.remote_addr}",
                   extra={"error": str(e)},
               )
   ```

4. **Supports Testing**: Uses dependency injection for I/O functions
   ```python
   def __attrs_post_init__(self) -> None:
       """
       Initialize with default I/O functions if not provided.
       """
       if self.send_func is None:
           self.send_func = self._default_send
       if self.receive_func is None:
           self.receive_func = self._default_receive
   ```

---

## Implementation Priorities

The implementation should proceed in this order:

1. **Core Abstractions**
   - Base interfaces for transport, protocol, and handlers
   - Exception hierarchy for clear error reporting
   - Configuration system for flexible settings

2. **Transport Layer**
   - TCP transport implementation
   - Unix socket transport implementation
   - Transport negotiation mechanism
   - Client connection management

3. **Protocol Definition**
   - Protocol buffer definitions
   - gRPC service interfaces
   - Handler interface

4. **Security Components**
   - Certificate generation and validation
   - Handshake message format
   - Magic cookie validation
   - TLS channel configuration

5. **Server Implementation**
   - Server setup and configuration
   - Transport initialization
   - Protocol registration
   - Lifecycle management

6. **Client Implementation**
   - Connection management
   - Service stub creation
   - Error handling and recovery
   - Resource cleanup

7. **Integration Components**
   - Go-bridge implementation
   - Process management
   - IO proxying

8. **Testing Framework**
   - Unit tests for all components
   - Integration tests with Terraform
   - Test mocks and fixtures

---

## Compatibility Strategy

Maintaining compatibility with Terraform is critical for the Pyvider RPC Plugin system.

### Terraform Protocol Compatibility

The implementation must follow Terraform's plugin protocol exactly:

1. **Protocol Version Support**:
   - Support all current and recent protocol versions
   - Implement proper version negotiation
   - Handle backward compatibility for older versions

2. **Message Format Compliance**:
   - Implement exact protocol buffer definitions
   - Follow all serialization requirements
   - Match Terraform's wire format expectations

3. **Service Implementation**:
   - Implement all required gRPC services
   - Follow Terraform's behavior semantics
   - Handle error states correctly

### Handshake Process Compliance

The handshake process is especially critical for compatibility:

1. **Magic Cookie Validation**:
   - Match Terraform's cookie validation
   - Handle environment-based cookies correctly
   - Provide proper error reporting for mismatches

2. **Handshake Response Format**:
   - Follow the exact pipe-delimited format
   - Include all required fields
   - Format certificate data correctly

3. **Transport Address Format**:
   - Use correct formats for TCP addresses
   - Use correct formats for Unix socket paths
   - Handle platform-specific path requirements

### Go/Python Interoperability

Special attention is needed for Go/Python interoperability:

1. **Process Communication**:
   - Handle differences in IO buffering
   - Manage encoding differences
   - Deal with different line ending conventions

2. **Type Conversion**:
   - Handle numeric precision differences
   - Manage string encoding differences
   - Deal with collection type differences

3. **Exception Handling**:
   - Map Python exceptions to Go error codes
   - Provide detailed error context
   - Ensure proper error propagation

### Testing Against Terraform

Regular testing against actual Terraform installations is essential:

1. **Integration Tests**:
   - Test with multiple Terraform versions
   - Test on all supported platforms
   - Test with real-world provider implementations

2. **Compatibility Validation**:
   - Validate protocol version negotiation
   - Verify handshake success
   - Test with and without mTLS

3. **Edge Case Testing**:
   - Test error conditions and recovery
   - Test unusual configurations
   - Test resource limits

By following these strategies, the Pyvider RPC Plugin system can maintain robust compatibility with Terraform while providing a Pythonic implementation that leverages modern Python features.