
import java.awt.*;
import java.awt.event.*;
import java.applet.*;
import java.io.*;


public class DemoApplet extends Applet
implements SMILListener
{
    private Frame frame = null;
    private SMILPlayer player;
    private Viewport viewport;
	public void init()
	{
		// This code is automatically generated by Visual Cafe when you add
		// components to the visual environment. It instantiates and initializes
		// the components. To modify the code, only use code syntax that matches
		// what Visual Cafe can generate, or Visual Cafe may be unable to back
		// parse your Java file into its visual environment.
		//{{INIT_CONTROLS
		setLayout(null);
		setSize(480,106);
		buttonOpen.setLabel("Open");
		add(buttonOpen);
		buttonOpen.setBackground(java.awt.Color.lightGray);
		buttonOpen.setBounds(368,8,104,28);
		labelOpen.setText("Open:");
		add(labelOpen);
		labelOpen.setBounds(12,12,40,24);
		add(textFieldURL);
		textFieldURL.setBounds(57,8,311,28);
		buttonPlay.setLabel("Play");
		add(buttonPlay);
		buttonPlay.setBackground(java.awt.Color.lightGray);
		buttonPlay.setBounds(8,56,104,28);
		buttonPause.setLabel("Pause");
		add(buttonPause);
		buttonPause.setBackground(java.awt.Color.lightGray);
		buttonPause.setBounds(128,56,104,28);
		buttonStop.setLabel("Stop");
		add(buttonStop);
		buttonStop.setBackground(java.awt.Color.lightGray);
		buttonStop.setBounds(248,56,104,28);
		buttonClose.setLabel("Close");
		add(buttonClose);
		buttonClose.setBackground(java.awt.Color.lightGray);
		buttonClose.setBounds(368,56,104,28);
		//}}
	
	    player = GRiNSToolkit.createGRiNSPlayer(this);

		//{{REGISTER_LISTENERS
		SymAction lSymAction = new SymAction();
		buttonOpen.addActionListener(lSymAction);
		buttonPlay.addActionListener(lSymAction);
		buttonPause.addActionListener(lSymAction);
		buttonStop.addActionListener(lSymAction);
		buttonClose.addActionListener(lSymAction);
		//}}
	}
	
	//{{DECLARE_CONTROLS
	java.awt.Button buttonOpen = new java.awt.Button();
	java.awt.Label labelOpen = new java.awt.Label();
	java.awt.TextField textFieldURL = new java.awt.TextField();
	java.awt.Button buttonPlay = new java.awt.Button();
	java.awt.Button buttonPause = new java.awt.Button();
	java.awt.Button buttonStop = new java.awt.Button();
	java.awt.Button buttonClose = new java.awt.Button();
	//}}
	
	private void message(String str) {
	    System.out.println(str+"\n");
	}
	
	public void start() {
	    }
	public void stop() {
	    if(player!=null) player.close();
	    }
    public void destroy() {
        }
    public void setWaiting(){
        setCursor(new Cursor(Cursor.WAIT_CURSOR));
    }
    public void setReady(){
       setCursor(Cursor.getDefaultCursor());
    }
	  
	// standalone execution support
    public static void main(String args[]) 
		{
	    class SFrame extends Frame {
	        SFrame(String title){
	            super(title);
	            }
	        void setApplet(Applet p){
	            applet = p;
	            }
	        private Applet applet;
	        }
		SFrame frame = new SFrame("Java GRiNS Player");
		frame.addWindowListener(
			new WindowAdapter() { 
				public void windowClosing(WindowEvent e) {
				    ((SFrame)e.getWindow()).applet.stop();
			        System.exit(0);
			        }
				});
	
		DemoApplet	demoApplet = new DemoApplet();
        frame.setApplet(demoApplet);
		demoApplet.init();
		demoApplet.start();
		frame.add("Center", demoApplet);
        frame.pack();
		frame.setSize(480+8,106+24);
		frame.setLocation(400,300);
		frame.show();
		}
	

	class SymAction implements java.awt.event.ActionListener
	{
		public void actionPerformed(java.awt.event.ActionEvent event)
		{
			Object object = event.getSource();
			if (object == buttonOpen)
				buttonOpen_ActionPerformed(event);
			else if (object == buttonPlay)
				buttonPlay_ActionPerformed(event);
			else if (object == buttonPause)
				buttonPause_ActionPerformed(event);
			else if (object == buttonStop)
				buttonStop_ActionPerformed(event);
			else if (object == buttonClose)
				buttonClose_ActionPerformed(event);
		}
	}

	void buttonOpen_ActionPerformed(java.awt.event.ActionEvent event)
	{
		FileDialog dlg = new FileDialog((Frame)getParent(), "Select presentation", FileDialog.LOAD);
		dlg.show();
		String filename = dlg.getFile();
		if(filename!=null){
		    String dir  = dlg.getDirectory();
		    String absFilename = dir+filename;
		    textFieldURL.setText(absFilename);
		}
		if(player!=null){
		    PlayerCanvas canvas = new PlayerCanvas();
	        viewport = new Viewport(canvas);
	        player.setCanvas(canvas);
		    player.open(textFieldURL.getText());
	    }
		
	}

    // implement interface of SMILListener
    public void opened(){
    }
    public void closed(){
        viewport.setVisible(false);
        viewport.dispose();
        viewport = null;
    }
    public void setViewportSize(int w, int h){
        viewport.update(w, h);
    }
    
    
	void buttonPlay_ActionPerformed(java.awt.event.ActionEvent event)
	{
		// to do: code goes here.
		if(player!=null) player.play();
	}

	void buttonPause_ActionPerformed(java.awt.event.ActionEvent event)
	{
		// to do: code goes here.
		if(player!=null) player.pause();
	}

	void buttonStop_ActionPerformed(java.awt.event.ActionEvent event)
	{
		// to do: code goes here.
		if(player!=null) player.stop();
	}

	void buttonClose_ActionPerformed(java.awt.event.ActionEvent event)
	{
		// to do: code goes here.
		if(player!=null)player.close();
	}

}
