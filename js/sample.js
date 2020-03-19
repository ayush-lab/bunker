
var click=0;
for ( var i=0;i<document.querySelectorAll("td").length;i++)
{
document.querySelectorAll("td")[i].addEventListener("click",function()
{

		this.innerHTML='<i class="far fa-check-circle"></i>';
	     
	


})

}