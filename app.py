import time
import sched

from measure import main


if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)

    def run_main(scheduler):
        main()
        scheduler.enter(60, 1, run_main, (scheduler,))

    run_main(scheduler)
    scheduler.run()