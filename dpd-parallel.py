import multiprocessing
import os
import platform

# List of dmpci files to run in parallel
# dmpcis = ["folder/dmpci.1",
#           "folder/folder2/dmpci.2"]
dmpcis = []


class Simulation(multiprocessing.Process):
    def __init__(self, dmpci):
        multiprocessing.Process.__init__(self)
        self.dmpci = dmpci
        self.path = self.dmpci[:self.dmpci.find("dmpci.")]
        self.file = self.dmpci[self.dmpci.find("dmpci."):]
        self.ID = self.file[self.file.find(".")+1:]

    def run(self):
        print(f"[{self.dmpci}] running ... process ID: {os.getpid()}")
        cwd = os.getcwd()
        os.chdir(self.path)

        if platform.system().lower() == 'windows':
            os.system(f"dpd-w10.exe {self.ID}")
        else:
            os.system(f'dpd-linux {self.ID}')

        os.chdir(cwd)


def compute(dmpcis):
    simulations = [Simulation(dmpci) for dmpci in dmpcis]

    for simulation in simulations:
        simulation.start()


if __name__ == "__main__":
    compute(dmpcis)
