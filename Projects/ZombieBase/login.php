
<!-- 

Did you discover this server by accident?

The web GUI for managing my Overwatch & Paladins aimbot(Private Software).

thehandoflinux@gmail.com

         _nnnn_
        dGGGGMMb
       @p~qp~~qMb
       M|@||@) M|
       @,____.JM|
      JS^\__/  qKL
     dZP        qKRb
    dZP          qKKb
   fZP            SMMb
   HZM            MMMM
   FqM            MMMM
 __| ".        |\dS"qML
 |    `.       | `' \Zq
_)      \.___.,|     .'
\____   )MMMMMP|   .'
     `_'       `_' 

-->

<!DOCTYPE html>
<html>
<head>
	<title>Invalid Login</title>

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
  <a href="index.php" class="w3-bar-item w3-button">Main</a>
  <a href="#" onClick="alert('This panel is private.')" class="w3-bar-item w3-button">About</a>
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
  <h1>Invalid login credentials.</h1>
</div>
</div>

<div class="container-fluid">
	
	<div class="row">
		<div class="col-md-6 animated fadeInLeft">
			<h4 title="Login to access dashboard.">Login</h4>
			<div class="space1">
			<!-- Start Login -->
        <form action="login.php" method="post">
          Username: <input type="text" name="uname" class="inputSel"><br>
          Password: <input type="password" name="pword" class="inputSel" title="Hint: 41 71 75 61"><br>
          <input type="submit" value="Login" class="logbtn">
        </form>
			<!-- End Login -->
			</div>
		</div>

    <div class="col-md-6 animated fadeInRight">
      <h4>Dashboard Tunes - <a title="Click Here to learn about 'Dashboard Tunes'" onClick="alert('Just some relaxing music.');">[?]</a></h4>
      
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
		<div class="col-md-12 animated fadeInLeft">
		  <h4 title="Login to access terminal.">Command</h4>
			<div class="space2">
        <div class="cli">
          <div class="cli-body" ng-click="focusTextarea()">
            <p>
              <!-- Terminal is offline until you login -->
              <span class="dollar">$</span> Please enter a command (Offline):
            </p>

            <div class="cli-control">
              <span class="dollar left">$</span>
              <input type="text" class="cli-input right" name="cli-input" autofocus>
            </div>
          </div>
        </div>
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

<!-- JQuery Self Typing Text Animation -->
<script type="text/javascript">
var str = 'Type "help" for a list of commands.';

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

  $('.cli-body').click(function() {
    $('.cli-input').focus();
  });

  // Commands removed... Gotta login for that you silly goose.

  $('.cli-input').on('change', function() {
    if($(this).val()=="help")
    {
      $('.cli-control').before('<p class="success">= Commands =<br>Please authenticate to use terminal...<br></p>');
    }
    else
    {
      $('.cli-control').before('<p class="error"><span class="dollar">$</span> ' + $(this).val() + '</p>');
    }

    $(this).val('');

    // AJAX/JSON removed.. No communicating with MySQL DB from this page. Gotta login silly...

  });
});

</script>


<?php

$username = $_POST['uname'];
$password = $_POST['pword'];

if($username=="admin" && $password=="sethbrundle")
{
	?><script>window.location="144758.php"</script><?php
	exit;
}
else
{
	
}
?>
