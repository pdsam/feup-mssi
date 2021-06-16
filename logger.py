class Logger:
    step = 0
    firstLog = True
    active = True

    def setActive(active):
        Logger.active = active
    
    def resetStep():
        Logger.step = 0
        Logger.firstLog = True

    def incrementStep():
        Logger.step += 1
        Logger.firstLog = True
    
    def log(message):
        if not Logger.active:
            return

        if Logger.firstLog:
            print(f"\nstep {Logger.step}:")
            Logger.firstLog = False
        print(f"\t{message}")

