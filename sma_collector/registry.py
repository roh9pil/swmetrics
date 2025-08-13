from typing import Dict, Callable, Type
from sma_collector.connectors.collector import BaseCollector

CONNECTOR_REGISTRY: Dict[str, Type[BaseCollector]] = {}
PROCESSOR_REGISTRY: Dict[str, Callable] = {}

def register_connector(source: str, connector_class: Type[BaseCollector]):
    """Registers a connector class for a given source."""
    CONNECTOR_REGISTRY[source] = connector_class

def register_processor(source: str, processor_function: Callable):
    """Registers a data processing function for a given source."""
    PROCESSOR_REGISTRY[source] = processor_function
