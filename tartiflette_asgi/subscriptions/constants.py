class GQL:
    # Client -> Server message types.
    CONNECTION_INIT = "connection_init"
    START = "start"
    STOP = "stop"
    CONNECTION_TERMINATE = "connection_terminate"

    # Server -> Client message types.
    CONNECTION_ERROR = "connection_error"
    CONNECTION_ACK = "connection_ack"
    DATA = "data"
    ERROR = "error"
    COMPLETE = "complete"
    CONNECTION_KEEP_ALIVE = "ka"
