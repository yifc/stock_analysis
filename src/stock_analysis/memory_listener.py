from crewai.events import (
    BaseEventListener,
    MemoryQueryCompletedEvent,
    MemorySaveCompletedEvent,
    MemorySaveFailedEvent,
    MemoryQueryFailedEvent
)
import logging

# Configure logging to also show in console if not already configured
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('stock_memory')

class StockMemoryListener(BaseEventListener):
    """Monitors memory operations for stock analysis crew"""
    
    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(MemorySaveCompletedEvent)
        def on_save(source, event):
            logger.info(f"💾 Memory saved: {event.value[:100]}...")
        
        @crewai_event_bus.on(MemoryQueryCompletedEvent)  
        def on_query(source, event):
            logger.info(f"🔍 Memory query: '{event.query}' (Time: {event.query_time_ms:.1f}ms)")

        @crewai_event_bus.on(MemorySaveFailedEvent)
        def on_save_failed(source, event):
            logger.error(f"❌ Memory save failed: {event.error}")

        @crewai_event_bus.on(MemoryQueryFailedEvent)
        def on_query_failed(source, event):
            logger.error(f"❌ Memory query failed: {event.error}")
