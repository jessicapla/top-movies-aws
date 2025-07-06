from typing import TypedDict, List, Dict, Optional

class SQSMessageAttributes(TypedDict):
    stringValue: Optional[str]
    binaryValue: Optional[str]
    dataType: str

class SQSAttributes(TypedDict):
    ApproximateReceiveCount: str
    SentTimestamp: str
    SenderId: str
    ApproximateFirstReceiveTimestamp: str

class SQSRecord(TypedDict):
    messageId: str
    receiptHandle: str
    body: str
    attributes: SQSAttributes
    messageAttributes: Dict[str, SQSMessageAttributes]
    md5OfBody: str
    eventSource: str  # "aws:sqs"
    eventSourceARN: str
    awsRegion: str

class SQSEvent(TypedDict):
    Records: List[SQSRecord]
