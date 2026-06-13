from collections import deque
import sqlite3

class MicroBatcher:
    def __init__(self):
        self.buffer=deque()
    def add(self,record):
        self.buffer.append(record)

    def flush(self):
        batch=[]
        while self.buffer:
            item=self.buffer.popleft()
            batch.append(item)
        return batch
    def DatabaseSink(self):
        print(f"Writing to database")
        #create a database
        conn=sqlite3.connect("telemetry.db")
        #create a cursor
        cursor=conn.cursor()
        try:
            cursor.execute("""
            create table if not exists telemetry(
            id INTEGER PRIMARY KEY,
            message TEXT
            )
            """)
            data=[(i,)for i in self.buffer]
            cursor.executemany(f"INSERT INTO telemetry (message) values(?)",data)
            conn.commit()
        except Exception as e:
            print(f"Error writing to database")
        finally:
            conn.close()
            print(f"closed")
    def databaseselect(self):
        print(f"reading data from database")    
        try:
            conn=sqlite3.connect("telemetry.db")
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM telemetry")
            rows=cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error reading from database")
        finally:
            conn.close()
            print(f"closed")

if __name__=="__main__":
    batcher=MicroBatcher()
    batcher.add("record_1")
    batcher.add("record_2")
    batcher.add("record_3")
    batcher.DatabaseSink()
     # Flush should return the list of items and empty the deque
    print("Flushed batch:", batcher.flush())  # Expected: ['record_1', 'record_2']
    print("Buffer size after flush:", len(batcher.buffer))  # Expected: 0
    data=batcher.databaseselect()
    print(f"number of records in database:{len(data)}")
    
            
