import random
import math
from multiprocessing import Process, Queue
from multiprocessing import Lock

def calculateMean(data):
    totalSum = 0
    for value in data:
        totalSum += value
    meanValue = totalSum / len(data)
    return meanValue

def calculatePartialSum(dataChunk, queue, lock):
    meanValue = calculateMean(dataChunk)
    partialSum = sum((x - meanValue) ** 2 for x in dataChunk)
    with lock:
        queue.put((partialSum, len(dataChunk)))

def calculateStandardDeviation(data):
    chunkSize = len(data) // 2
    chunks = [data[:chunkSize], data[chunkSize:]]
    
    queue = Queue()
    lock = Lock()
    
    process1 = Process(target=calculatePartialSum, args=(chunks[0], queue, lock))
    process2 = Process(target=calculatePartialSum, args=(chunks[1], queue, lock))
    
    process1.start()
    process2.start()
    
    process1.join()
    process2.join()
    
    totalSum = 0
    totalCount = 0

    while not queue.empty():
        partialSum, count = queue.get()
        totalSum += partialSum
        totalCount += count
    
    overallMean = calculateMean(data)
    variance = totalSum / totalCount
    standardDeviation = math.sqrt(variance)
    
    return standardDeviation

def findWordIndices(textChunk, word, queue, lock, offset):
    indices = []
    words = textChunk.split()
    for i in range(len(words)):
        if words[i] == word:
            indices.append(i + offset)
    with lock:
        queue.put(indices)

def parallelFindWordIndices(text, word):
    words = text.split()
    chunkSize = len(words) // 2
    chunks = [' '.join(words[:chunkSize]), ' '.join(words[chunkSize:])]
    
    queue = Queue()
    lock = Lock()
    
    process1 = Process(target=findWordIndices, args=(chunks[0], word, queue, lock, 0))
    process2 = Process(target=findWordIndices, args=(chunks[1], word, queue, lock, chunkSize))
    
    process1.start()
    process2.start()
    
    process1.join()
    process2.join()
    
    indices = []
    while not queue.empty():
        indices.extend(queue.get())
    
    return indices

def exec():
    data = [random.random() * 100 for _ in range(500)]
    stdDev = calculateStandardDeviation(data)
    print(f"Standard Deviation: {stdDev}")

    text = """
    This is a sample text with several words. This text is for testing. 
    The purpose of this text is to test the functionality of the code. 
    This text contains many words, and some words repeat multiple times. 
    For example, the word 'text' appears several times in this text. 
    The word 'words' also appears multiple times. 
    This is to ensure that the code can handle texts with repeating words. 
    By repeating words, we can test the accuracy of the code. 
    This text is designed to be a comprehensive test case. 
    The word 'test' is another word that appears multiple times in this text. 
    Overall, this text is a good example of a text with repeating words and means absolutely nothing.
    """
    word = "text"
    indices = parallelFindWordIndices(text, word)
    print(f"Indices of '{word}': {indices}")

if __name__ == "__main__":
    exec()