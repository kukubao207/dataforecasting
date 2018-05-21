package cumt.wjq.util;

import cumt.wjq.model.Agent;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;


public class PythonData {
    public static List<Agent> getPythonData(String path) throws IOException{
        List<Agent> agentList= new ArrayList<>();
        if(!new File(path).exists())
            return null;
        Scanner scanner = new Scanner(new FileReader(path));
        while(scanner.hasNextLine()) {
            Agent agent = new Agent();
            String record = scanner.nextLine();
            if(record.isEmpty())
                break;
//            System.out.println(record);
            String[] elements = record.split(",");
            agent.setDayId(Integer.parseInt(elements[0]));
            agent.setRank(Integer.parseInt(elements[1]));
            agent.setNbr(elements[2]);
            agent.setSumCnt(Integer.parseInt(elements[3]));
            agent.setSumRound(Integer.parseInt(elements[4]));
            agent.setIndeg(Integer.parseInt(elements[5]));
            agent.setOutdeg(Integer.parseInt(elements[6]));
            agent.setPagerankValue(Float.parseFloat(elements[7]));
            agentList.add(agent);
        }
        return agentList.size()>0?agentList:null;
    }
}
