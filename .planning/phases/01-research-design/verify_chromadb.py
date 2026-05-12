#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import tempfile
import shutil

def verify_chromadb():
    try:
        import chromadb
        from chromadb.config import Settings
        print('ChromaDB version:', chromadb.__version__)
        print('Installation: success')
    except ImportError as e:
        print('Installation: failed -', e)
        print('Please run: pip install chromadb')
        return {'status': 'failed', 'error': 'chromadb not installed'}

    temp_dir = tempfile.mkdtemp(prefix='chromadb_test_')
    print('Using temp directory:', temp_dir)

    try:
        client = chromadb.PersistentClient(path=temp_dir)
        
        collection = client.get_or_create_collection(
            name='test_collection',
            metadata={'hnsw:space': 'cosine'}
        )
        print('Collection created: success')

        import random
        num_vectors = 1000
        dimension = 128
        
        embeddings = [[random.random() for _ in range(dimension)] for _ in range(num_vectors)]
        documents = ['Document ' + str(i) for i in range(num_vectors)]
        ids = ['id_' + str(i) for i in range(num_vectors)]
        metadatas = [{'source': 'test', 'index': i} for i in range(num_vectors)]

        start = time.perf_counter()
        collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        add_time = (time.perf_counter() - start) * 1000
        print('Add', num_vectors, 'vectors:', round(add_time, 2), 'ms')

        query_latencies = []
        for i in range(10):
            query_embedding = [random.random() for _ in range(dimension)]
            start = time.perf_counter()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5
            )
            query_time = (time.perf_counter() - start) * 1000
            query_latencies.append(query_time)

        query_latencies.sort()
        p50 = query_latencies[len(query_latencies) // 2]
        p95 = query_latencies[int(len(query_latencies) * 0.95)]
        
        print('Query P50 latency:', round(p50, 2), 'ms')
        print('Query P95 latency:', round(p95, 2), 'ms')

        count = collection.count()
        print('Document count:', count)

        collection.delete(ids=['id_0', 'id_1'])
        new_count = collection.count()
        print('After delete count:', new_count)

        return {
            'status': 'success',
            'version': chromadb.__version__,
            'p50_latency_ms': p50,
            'p95_latency_ms': p95,
            'vectors_tested': num_vectors
        }

    except Exception as e:
        print('Error:', e)
        return {'status': 'failed', 'error': str(e)}

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print('Cleaned up temp directory:', temp_dir)

if __name__ == '__main__':
    result = verify_chromadb()
    print()
    print('Final result:', result)
