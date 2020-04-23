const dark=document.getElementById("dark_1");
const azure=document.getElementById("azure_1");
const main_c=document.getElementById("container-fluid-id");
var contain=document.getElementById("container2");

const intro=document.getElementById("intro");

const edit_img =document.getElementById("edit_img");

const college=document.getElementById("college");
const college_img =document.getElementById("college_img");
const status =document.getElementById("status");
const status_img =document.getElementById("status_img");
const timetabletitle=document.getElementById("timetabletitle");
const table=document.getElementById("table");

// selected theme variaable
console.log("connected");
console.log(localStorage.getItem("theme"));


var selected_theme = localStorage.getItem("theme");

if(selected_theme=="azure")
	{
	
	console.log("working---azure");
	 azure_theme();

azure.addEventListener("click", azure_theme);
dark.addEventListener("click",dark_theme);
    
    }

if(selected_theme=="dark"){
	console.log("dark -- theme");
	dark_theme();



azure.addEventListener("click", azure_theme);
dark.addEventListener("click",dark_theme);
}

function azure_theme(){

	selected_theme="azure";
	localStorage.removeItem("theme",selected_theme);
	localStorage.setItem("theme",selected_theme);

	main_c.classList.remove("dark-container-fluid");
	contain.classList.remove("dark");

	main_c.classList.add("normal-container-fluid");
	contain.classList.add("normal");

	intro.classList.remove("dark-text");
	intro.classList.add("normal-text");

	
	college.classList.remove("dark-text");
	college.classList.add("normal-text");

	status.classList.remove("dark-text");
	status.classList.add("normal-text");


	college_img.classList.remove("dark-image");
	college_img.classList.add("normal-image");


	status_img.classList.remove("dark-image");
	status_img.classList.add("normal-image");

	timetabletitle.classList.remove("dark-text");
	timetabletitle.classList.add("normal-text");

	table.classList.remove("dark-text");
	table.classList.add("normal-text");
	
	edit_img.classList.remove("dark-image");
	edit_img.classList.add("normal-image");
}

function dark_theme(){

	console.log("working_dark");
	selected_theme = "dark";

	localStorage.removeItem("theme",selected_theme);
	localStorage.setItem("theme",selected_theme);

	main_c.classList.remove("normal-container-fluid");
	contain.classList.remove("normal");
	main_c.classList.add("dark-container-fluid");
	contain.classList.add("dark");

	intro.classList.remove("normal-text");
	intro.classList.add("dark-text");
	
	college.classList.remove("normal-text");
	college.classList.add("dark-text");

	status.classList.remove("normal-text");
	status.classList.add("dark-text");


	college_img.classList.remove("normal-image");
	college_img.classList.add("dark-image");


	status_img.classList.remove("normal-image");
	status_img.classList.add("dark-image");

	timetabletitle.classList.remove("normal-text");
	timetabletitle.classList.add("dark-text");

	table.classList.remove("normal-text");
	
	table.classList.add("dark-text");
	
	edit_img.classList.remove("normal-image");
	edit_img.classList.add("dark-image");
}