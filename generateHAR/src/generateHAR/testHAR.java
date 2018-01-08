package generateHAR;

import static org.junit.jupiter.api.Assertions.*;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.openqa.selenium.Proxy;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.remote.CapabilityType;

import net.lightbody.bmp.BrowserMobProxyServer;
import net.lightbody.bmp.client.ClientUtil;
import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.CaptureType;

class testHAR {

	@Test
	void test() {
		
	    //String site;
	    String site = "google.de";
	    
	    //String filename = "/home/rohit/chromedriver/web-7";
	    String filename = "/home/rohit/chromedriver/web-1";
	    List<String> records = new ArrayList<String>();
	    
	    try {
	    	BufferedReader reader = new BufferedReader(new FileReader(filename));
	    	String line;
	    	while((line = reader.readLine()) != null)
	    	{
	    		records.add(line);
	    	}
	    	reader.close();
	    } catch(Exception e) {
	    	System.err.format("Exception occured trying to read %s file", filename);
	    }
	    
	    for(int i=0; i < records.size(); i++)
	    {
	    	site = records.get(i);
	    
		System.setProperty("webdriver.chrome.driver","/usr/bin/chromedriver");
		BrowserMobProxyServer proxy = new BrowserMobProxyServer();
	    proxy.start(0);
	    Proxy seleniumProxy = ClientUtil.createSeleniumProxy(proxy);
	    ChromeOptions chromeOptions = new ChromeOptions();
	    chromeOptions.addArguments("user-data-dir=/home/rohit/.config/google-chrome/");
	    chromeOptions.setCapability(CapabilityType.PROXY, seleniumProxy);
	    chromeOptions.addExtensions(new File("/home/rohit/chromedriver/adblockpluschrome-3.0.2.1948.crx"));

	    WebDriver driver = new ChromeDriver(chromeOptions);

	    // enable more detailed HAR capture, if desired (see CaptureType for the complete list)
	    proxy.enableHarCaptureTypes(CaptureType.REQUEST_CONTENT, CaptureType.RESPONSE_CONTENT);
    
	    proxy.newHar(site);

	    // open site
	    driver.get("http://"+site);
	    try        
	    {
	        Thread.sleep(5000);
	    } 
	    catch(InterruptedException ex) 
	    {
	        Thread.currentThread().interrupt();
	    }
	    
	    String source = driver.getPageSource();

	    // get the HAR data
	    Har har = proxy.getHar();

	    System.out.println("Entries count :"+  har.getLog().getEntries().size());
	    File harFile = new File(site+".har");
	    
	    try(  PrintWriter out = new PrintWriter( site+".html" )  ){
	        out.println( source );
	    }catch(Exception e){
	    	e.printStackTrace();
	    }
	    
	    try{
	    harFile.createNewFile();
	    har.writeTo(harFile);
	    }catch(Exception e){
	    	e.printStackTrace();
	    }
	    
	    proxy.stop();
	    driver.quit();
	    }
	}

}
