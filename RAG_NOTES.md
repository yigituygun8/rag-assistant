# RAG Notes

Retrieval Augmented Generation (RAG) is a method that combines retrieval-based and generation-based approaches in natural language processing. It allows models to retrieve relevant information from a large corpus of documents and use that information to generate more accurate and contextually appropriate responses. This approach is particularly useful in tasks such as question answering, summarization, and dialogue systems, where access to external knowledge can significantly enhance the quality of generated content.

## Core Idea

- **Retrieval**: The model searches through a large collection of documents to find relevant information based on the input query. This is typically done using techniques such as vector embeddings, where both the query and documents are represented in a high-dimensional space, allowing for efficient similarity searches. The retrieved documents serve as a knowledge base that informs the generation process.
- **Augmenting**: The model uses the retrieved documents to generate responses. This can involve incorporating specific facts, context, or examples from the retrieved information into the generated text. The generation process can be guided by various techniques, such as attention mechanisms or prompt engineering, to ensure that the output is coherent and relevant to the input query.
- **Generation**: The final output is produced based on the augmented information. This can be done using various generative models, such as transformers, which are capable of generating human-like text. The model can leverage the retrieved knowledge to produce responses that are not only accurate but also contextually rich and informative.

## When Not To Use RAG

While RAG can be highly effective in many scenarios, there are situations where it may not be the best approach. For instance, if the input query is highly specific and does not require external knowledge, a purely generative model may suffice. Additionally, if the retrieval process is slow or the corpus is not well-curated, it may lead to irrelevant or low-quality information being used in the generation phase. In such cases, alternative methods or models may be more appropriate.

## Safety And Quality Rules

There should be restrictions / security rules in place to ensure that the retrieved information is accurate, relevant, and does not contain sensitive or harmful content. This may involve implementing filters, validation checks, and ethical guidelines to govern the retrieval and generation processes. Prompt engineering can be used to ensure that the model adheres to these rules and produces safe and reliable outputs.

## Fine-Tuning Vs RAG

Fine-tuning is a crucial step in optimizing the performance of RAG models. It involves training the model on a specific dataset that is representative of the target domain or task. This allows the model to learn domain-specific knowledge and improve its ability to retrieve and generate relevant information. Fine-tuning can also help in adapting the model to specific user requirements, ensuring that the outputs are aligned with the desired style, tone, and content quality. It is great for stable, unchanging patterns like communication style but terrible for dynamic information that changes frequently, as the model may not be able to adapt quickly enough to new data because training is a time-consuming, costly process.

The best solution is usually a combination of RAG and fine-tuning, where the model can leverage retrieval for dynamic information at query time while also being fine-tuned for specific tasks or domains. This hybrid approach allows for flexibility and adaptability, ensuring that the model can provide accurate and contextually relevant responses even in rapidly changing environments.

## Approaches To Retrieval

1. **Keyword Search (Sparse Retrieval)**: Searches for exact matches of keywords or phrases between the query and documents. It relies on exact text token overlap and ranks results based on how often terms appear.
   - **TF-IDF** (Term Frequency-Inverse Document Frequency): Calculates the importance of a term in a document relative to its frequency in the entire corpus.
   - **BM25** (Best Matching 25): An extension of TF-IDF that adjusts for document length and prevents a word from artificially inflating a score if it repeats too many times. BM25 is the industry standard for keyword search and is more effective in retrieving relevant documents compared to TF-IDF.
2. **Semantic Search (Dense Retrieval)**: Searches for documents based on conceptual meaning, intent, and context rather than exact word matches. Deep learning models convert text into high-dimensional numerical lists called vector embeddings. This captures synonyms, translations, and broad intent, but can struggle with exact keyword matching, technical codes, or domain-specific jargon if the embedding model was not trained on it.
   - **Vector Search**: Uses spatial algorithms like cosine similarity, Euclidean distance, or dot product to find documents whose vectors are mathematically closest to the query vector.
3. **Hybrid Search**: Combines both keyword and semantic search techniques to leverage the strengths of each approach. It can provide more comprehensive results by first filtering documents using keyword search and then ranking them based on semantic relevance. This approach can help mitigate the weaknesses of each individual method, such as improving recall while maintaining precision. It is highly robust for production RAG systems, though it requires managing two separate indexing pipelines: a traditional database for keyword search and a vector database for semantic search. That makes it more complex to implement and maintain.
   - **RRF** (Reciprocal Rank Fusion): A method that combines the rankings from multiple retrieval systems, such as keyword and semantic search, by assigning scores based on the rank of each document in the individual systems. The final score for each document is calculated as the sum of the reciprocal of its rank across all systems, allowing for a more balanced and effective retrieval process.

## Re-Ranking

After retrieving a set of relevant documents, the next step is to re-rank them based on their relevance to the query. This can be done using various techniques, such as Cross-Encoder models, which evaluate the relevance of each document in relation to the query by processing them together. Re-ranking helps to ensure that the most relevant documents are prioritized for the generation phase, improving the overall quality of the generated responses.

### Retrieve Then Re-Rank Flow

User Query -> Stage 1 (Embedding Model - fast, searches millions of documents -> pulls top N documents) -> Stage 2 (Cross-Encoder - accurate but very slow, compares those N side-by-side with the query -> sorts out the absolute best M documents) -> Top M documents are passed to the generator (LLM) for response generation.

## Embeddings

An embedding is a numerical representation of text or other data in a high-dimensional space. It captures the semantic meaning of the text, allowing for comparisons and similarity calculations. Embeddings are typically generated using deep learning models, such as transformers, and can be used for various tasks, including retrieval, clustering, and classification. In the context of RAG, embeddings are crucial for enabling semantic search and improving the relevance of retrieved documents.

- **Use cases**: Search, recommendation, clustering, classification, and anomaly detection. Embeddings can also be used to represent other types of data, such as images or audio, allowing for multimodal retrieval and generation tasks.
- **Example models**: OpenAI's text-embedding-ada-002, Cohere's embed-multilingual-v2.0, and Hugging Face's all-MiniLM-L6-v2. Each model has its own strengths and weaknesses, and the choice of embedding model can significantly impact the performance of the RAG system.

## Vector Databases

Vector databases are specialized databases designed to store and manage high-dimensional vector embeddings. They provide efficient indexing and retrieval capabilities, allowing for fast similarity searches based on vector representations. In the context of RAG, vector databases are used to store the embeddings of documents, enabling the retrieval of relevant information based on semantic similarity. Popular vector databases include Chroma, Pinecone, Weaviate, Milvus, and FAISS (Facebook AI Similarity Search). These databases support various distance metrics and smart indexing techniques to optimize retrieval performance.

- **Indexing**: Pre-organizes the data into neighborhoods or clusters based on vector representations, which allows for faster retrieval by reducing the search space. This is crucial for handling large corpora of documents efficiently in a RAG system.
  - **HNSW** (Hierarchical Navigable Small World): A graph-based indexing method that organizes vectors into a hierarchical structure, enabling fast approximate nearest neighbor searches. Most vector databases use HNSW as their default indexing method due to its efficiency and scalability.
  - **IVF** (Inverted File Index): A method that partitions the vector space into clusters and creates an index for each cluster, allowing for efficient retrieval by only searching within relevant clusters.
  - **LSH** (Locality-Sensitive Hashing): A technique that hashes similar vectors into the same buckets, enabling fast retrieval by reducing the number of comparisons needed to find similar vectors.
- **Chroma**: An open-source vector database, lightweight and easy to use, designed for small to medium-sized datasets. It provides a simple API for storing and retrieving vector embeddings, making it suitable for prototyping and smaller RAG applications.
- **Pinecone**: A managed, serverless vector database service that offers scalability, high performance, and advanced features such as real-time updates and metadata support. It is designed for large-scale RAG applications and provides a user-friendly interface for managing vector data.

## Chunking

Chunking is the process of breaking down large documents into smaller, manageable pieces for processing. In the context of RAG, chunking is important because it allows the system to handle long documents that may exceed the input limits of the embedding model or LLM, or cases where someone asked for a specific piece of information but the whole document was returned, which is inefficient. By splitting documents into chunks, we can generate embeddings for each chunk and retrieve relevant information more effectively. Common chunking strategies include fixed-size chunks, semantic chunking based on sentence or paragraph boundaries, and overlapping chunks, where chunks have some overlap to preserve context. The choice of chunking strategy can impact the performance of the RAG system, as it affects the granularity of retrieval and the quality of generated responses.

### Chunking Best Practices

- **Size guidelines**: 200-500 characters, with 50-100 characters overlap. This may change based on the embedding model's input size and the nature of the documents. The goal is to balance having enough context in each chunk and not exceeding the model's input limits.
- **Boundary considerations**: Avoid splitting in the middle of sentences or paragraphs to maintain context and coherence.
- **Quality checks**: Test with real queries, verify context preservation, and ensure that chunks are meaningful and relevant to the task at hand.

## RAG Pipeline

A RAG pipeline is a structured workflow that integrates the retrieval and generation components of a RAG system. It typically consists of the following stages:

1. **Document ingestion**: The process of collecting and preparing documents for the RAG system. This may involve cleaning, formatting, and chunking the documents before generating embeddings.
2. **Embedding generation**: The stage where the system generates vector embeddings for the document chunks using an embedding model. These embeddings are then stored in a vector database for efficient retrieval.
3. **Retrieval**: When a user query is received, the system generates an embedding for the query and performs a similarity search against the stored document embeddings to retrieve relevant chunks of information.
4. **Re-ranking**: The retrieved chunks are re-ranked based on their relevance to the query, often using a more computationally intensive model such as a Cross-Encoder to ensure that the most relevant information is prioritized for the generation phase.
5. **Generation**: The final stage where the system uses the retrieved and re-ranked information as context to generate a response using a generative model (LLM). The generated response is then returned to the user.

## Caching

Caching is a technique used to store frequently accessed data in a temporary storage area to improve retrieval speed and reduce latency. In the context of RAG, caching can be applied at various stages of the pipeline, such as storing embeddings for frequently queried documents or caching generated responses for common queries. This can significantly enhance the performance of the system, especially in scenarios where certain queries are repeated often. Caching strategies may include time-based expiration, least recently used (LRU) eviction policies, and pre-computing embeddings for popular documents.

- We can implement caching at multiple levels of the RAG pipeline to optimize performance and reduce redundant computations. For example, we can cache the embeddings of frequently accessed documents, store the results of common queries, and even cache the generated responses from the LLM for repeated questions. This multi-level caching approach can help improve response times and reduce the computational load on the system.
- We can use in-memory caching solutions like Redis to store embeddings and query results, allowing for fast access and retrieval. Additionally, we can implement a caching layer within the application itself to manage the storage and retrieval of cached data efficiently.

## RAG In Production

When deploying a RAG system in a production environment, several considerations must be taken into account to ensure scalability, reliability, and maintainability. This includes monitoring system performance, implementing robust error handling, and ensuring that the retrieval and generation components are optimized for real-time processing. Additionally, security measures should be in place to protect sensitive data and prevent unauthorized access to the system. Regular updates and maintenance of the underlying models and databases are also essential to keep the RAG system effective and relevant over time.

- **Container orchestration**: Using containerization technologies like Docker and orchestration tools like Kubernetes can help manage the deployment of RAG systems in production. This allows for easy scaling, load balancing, and resource management, ensuring that the system can handle varying workloads efficiently.
  - **Data layer**: VectorDB, Redis, PostgreSQL, etc.
  - **RAG pipeline layer**: Query service, chunking, embeddings, retrieval, generation, augment service, routing, caching, re-ranking, etc.
  - **Application layer**: Frontend, backend, API gateway, etc.
  - **Monitoring stack**: Prometheus, Grafana, ELK Stack, etc. for monitoring system performance, logging, and alerting.