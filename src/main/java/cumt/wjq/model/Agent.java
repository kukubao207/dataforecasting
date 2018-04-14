package cumt.wjq.model;

public class Agent {
    private int dayId;
    private int rank;
    private String nbr;
    private int sumCnt;
    private int sumRound;
    private int indeg;
    private int outdeg;
    private float pagerankValue;

    public int getDayId() {
        return dayId;
    }

    public void setDayId(int dayId) {
        this.dayId = dayId;
    }

    public int getRank() {
        return rank;
    }

    public void setRank(int rank) {
        this.rank = rank;
    }

    public String getNbr() {
        return nbr;
    }

    public void setNbr(String nbr) {
        this.nbr = nbr;
    }

    public int getSumCnt() {
        return sumCnt;
    }

    public void setSumCnt(int sumCnt) {
        this.sumCnt = sumCnt;
    }

    public int getSumRound() {
        return sumRound;
    }

    public void setSumRound(int sumRound) {
        this.sumRound = sumRound;
    }

    public int getIndeg() {
        return indeg;
    }

    public void setIndeg(int indeg) {
        this.indeg = indeg;
    }

    public int getOutdeg() {
        return outdeg;
    }

    public void setOutdeg(int outdeg) {
        this.outdeg = outdeg;
    }

    public float getPagerankValue() {
        return pagerankValue;
    }

    public void setPagerankValue(float pagerankValue) {
        this.pagerankValue = pagerankValue;
    }
}
