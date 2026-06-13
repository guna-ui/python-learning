from collections import deque
import sqlite3
import time

class MicroBatcher:
    def __init__(self, batch_size=3, max_wait_seconds=2.0):
        self.buffer = deque()
        self.batch_size = batch_size
        self.max_wait_seconds = max_wait_seconds
        self.first_item_time = None

    def add(self, record):
        if not self.buffer:  
            self.first_item_time = time.time()
            
        self.buffer.append(record)
        
        if self.should_flush():
            batch = self.flush()       
            self.DatabaseSink(batch)   
            self.first_item_time = None

    def should_flush(self) -> bool:
        if len(self.buffer) >= self.batch_size:
            return True
            
        if self.buffer and self.first_item_time is not None:
            if time.time() - self.first_item_time >= self.max_wait_seconds:
                return True
                
        return False

    def flush(self):
        batch = []
        while self.buffer:
            item = self.buffer.popleft()
            batch.append(item)
        return batch

    def DatabaseSink(self, batch):  # Added batch parameter
        if not batch:
            return
        print(f"Writing {len(batch)} items to database")
        conn = sqlite3.connect("telemetry.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
            create table if not exists telemetry(
            id INTEGER PRIMARY KEY,
            message TEXT
            )
            """)
            data = [(i,) for i in batch]  # Iterate over batch instead of self.buffer
            cursor.executemany("INSERT INTO telemetry (message) values(?)", data)
            conn.commit()
        except Exception as e:
            print(f"Error writing to database: {e}")
        finally:
            conn.close()
            print("closed")

    def databaseselect(self):
        print("reading data from database")    
        try:
            conn = sqlite3.connect("telemetry.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM telemetry")
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error reading from database: {e}")
            return []
        finally:
            conn.close()
            print("closed")

if __name__ == "__main__":
    batcher = MicroBatcher(batch_size=3, max_wait_seconds=2.0)
    
    # --- TEST 1: Size-Based Auto-Flush ---
    print("--- Testing Size-Based Flush (limit = 3) ---")
    batcher.add("size_record_1")
    batcher.add("size_record_2")
    # This 3rd add should trigger DatabaseSink automatically:
    batcher.add("size_record_3") 
    print(f"Current buffer size: {len(batcher.buffer)}")  # Expected: 0
    
    # --- TEST 2: Time-Based Auto-Flush ---
    print("\n--- Testing Time-Based Flush (limit = 2.0s) ---")
    batcher.add("time_record_1")
    print("Waiting 2.5 seconds...")
    time.sleep(2.5)
    
    # Checking should_flush directly before adding next item
    if batcher.should_flush():
        print("Time limit exceeded! Flushing overdue batch...")
        batch = batcher.flush()
        batcher.DatabaseSink(batch)
        
    # Let's read the database to verify all records got saved
    all_records = batcher.databaseselect()
    print(f"\nTotal records now in database: {len(all_records)}")
