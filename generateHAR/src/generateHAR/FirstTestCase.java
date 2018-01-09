package generateHAR;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.remote.CapabilityType;
import org.openqa.selenium.Proxy;


import java.io.File;

import net.lightbody.bmp.BrowserMobProxyServer;
import net.lightbody.bmp.client.ClientUtil;
import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.CaptureType;

public class FirstTestCase {

	public static void main(String[] args) {
		System.setProperty("webdriver.chrome.driver","D:\\1 Rohit\\1 TUM\\Semester 3 - WS17\\Seminar\\code\\seminar-blocking-adblockers\\chromedriver_win32\\chromedriver.exe");
		BrowserMobProxyServer proxy = new BrowserMobProxyServer();
	    proxy.start(0);
	    Proxy seleniumProxy = ClientUtil.createSeleniumProxy(proxy);
	    ChromeOptions chromeOptions = new ChromeOptions();
	    chromeOptions.setCapability(CapabilityType.PROXY, seleniumProxy);
	    chromeOptions.addExtensions(new File("D:\\1 Rohit\\1 TUM\\Semester 3 - WS17\\Seminar\\code\\seminar-blocking-adblockers\\chromedriver_win32\\adblockpluschrome-3.0.2.1948.crx"));

	    WebDriver driver = new ChromeDriver(chromeOptions);

	    // enable more detailed HAR capture, if desired (see CaptureType for the complete list)
	    proxy.enableHarCaptureTypes(CaptureType.REQUEST_CONTENT, CaptureType.RESPONSE_CONTENT);

	    // create a new HAR with the label "yahoo.com"
	    // proxy.newHar("yahoo.com");

	    // open yahoo.com
	    driver.get("yahoo.de");

	    // get the HAR data
	    Har har = proxy.getHar();
	    
	    System.out.println("Entries count :"+  har.getLog().getEntries().size());
	    File harFile = new File("harfile.har");
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
