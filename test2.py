from multiprocessing import Pool 
import time 

def process(x):
    print("process" + str(x) + "started")
    time.sleep(x)
    print("process end")

if __name__ == "__main__":
    with Pool(4) as p:
        p.map(process, [1,2,3,4])
    print("main end")
