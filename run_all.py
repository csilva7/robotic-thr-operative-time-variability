"""Run the whole pipeline end to end: cohorts -> statistics -> figures."""
import analysis
import config as C
import data
import figures

if __name__ == '__main__':
    g = data.cohorts()
    print('Cohort sizes:', {k: len(v) for k, v in g.items()})
    analysis.main(g)
    figures.main(g)
    print('Outputs written to', C.OUT)
