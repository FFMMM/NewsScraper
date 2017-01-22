<?php
	$page = getActivePage();
	$navPages = ["home"=>"Publishers",
				 "day"=>"Day of Week",
				 "author"=>"Authors",
				 "section"=>"Sections"];
?>
<div class="container">
	<h1 class="display-3 d-flex justify-content-center p-5">NewsScraper Analysis</h1>
	<nav class="navbar navbar-toggleable-md navbar-light bg-faded">
		<button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
			<span class="navbar-toggler-icon"></span>
		</button>
		<div class="collapse navbar-collapse" id="navbarCollapse">
			<ul class="navbar-nav mx-auto">
				<?php
				foreach($navPages as $k=>$p){
					if($page == $k){print "<li class=\"nav-item active\">";}
					else{print "<li class=\"nav-item\">";}
					if($k == "home"){$k="";}
					print "<a class='nav-link' href='".getSubfolder()."/$k'>$p";
					if($k == ""){$k="home";}
					if($page == $k){print " <span class=\"sr-only\">(current)</span>";}
					print "</a></li>";
				}
				?>
			</ul>
		</div>
	</nav>
</div>

<?php
function getActivePage(){
	$path = explode('/', parse_url($_SERVER['REQUEST_URI'])["path"]);
	if(end($path) == ""){
		unset($path[count($path)-1]);
	}
	if("/".end($path) == getSubfolder() or end($path) == getSubfolder()){
		return "home";
	}
	return end($path);
}

function getSubfolder(){
	$path = explode('/', parse_url($_SERVER['REQUEST_URI'])["path"]);
	unset($path[count($path)-1]);
	$subfolder = implode($path, "/");
	return $subfolder;
}
?>