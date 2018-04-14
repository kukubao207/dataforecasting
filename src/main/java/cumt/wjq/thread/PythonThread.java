package cumt.wjq.thread;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;


public class PythonThread extends Thread
{
    private static final String pythonPath = "python";
    private String pyPath;
    private String arguments = null;
    public PythonThread(String pyPath)
    {
        this.pyPath = pyPath;
    }
    public PythonThread(String pyPath, String arguments)
    {
        this.pyPath=pyPath;
        this.arguments=arguments;
    }
    public void run()
    {
        try
        {
            //启动进程
            String command = pythonPath+" "+pyPath;
            String s;
            if(arguments!=null&&!arguments.equals(""))
            {
                command+=" "+arguments;
            }
            System.out.println(command);
            Process process = Runtime.getRuntime().exec(command);

            //在控制台输出进程的输出.
            BufferedReader stdInput = new BufferedReader(new InputStreamReader(process.getInputStream()));
            while ((s = stdInput.readLine()) != null)
            {
                System.out.println(s);
            }
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }
    }
}
