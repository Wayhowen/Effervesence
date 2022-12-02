import time

from evolve_basic import Evolve

if __name__ == "__main__":
    print("Setup...")
    start = time.time()
    # this for better pcs
    e = Evolve(4, 2, 1, 1000)
    #e = Evolve(10, 4, 2, 1000)

    tagger_q_table = []
    avoider_q_table = []
    try:
        print("Training Started...")
        best_tagger, best_avoider = e.work_dual(tagger_q_table, avoider_q_table)
        print("Training Complete")
        print("Best tagger:", repr(best_tagger[0].get_table()))
        print("Best avoider:", repr(best_avoider[0].get_table()))

        print("Score tagger:", best_tagger[1])
        print("Score avoider:", best_avoider[1])
        end = time.time()
        print("Time training:", end - start)
    finally:
        print("Saving...")
        e.save_table("tagger")
        e.save_table("avoider")
        e.save_stats("tagger")
        e.save_stats("avoider")
