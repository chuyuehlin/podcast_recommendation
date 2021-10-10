// $(function() {
// 	var boxTop = $('.container').offset().top + ($('.container').innerHeight()/2);
// 	setInterval(function(){
// 			// console.clear();
// 		$('.marquee img').each(function(index, el) {
// 			var imgTop = $(this).offset().top + ($(this).innerHeight()/2);
// 			var boxBg = $(this).attr('data-bgcolor');
// 			// console.log(boxTop, imgTop, imgId);
// 			if(imgTop <= boxTop){
// 				$('.container').css('background-color', boxBg);
// 			}
// 		});
// 	}, 100);
// });
let image_links;
const song = document.querySelector('#song');
const progressBar = document.querySelector('#outside'); // element where progress bar appears    
const outside = document.getElementById('outside');
const inside = document.getElementById('inside');
let pPause = document.querySelector('#play-pause'); // element where play and pause image appears

let playing = true;
let reco_event;
let reco_summ;

function playPause() {
    if (playing) {
        updateImage()
        updateSummary()
        reco_event = setInterval(updateImage, 15000);
        reco_summ = setInterval(updateSummary, 5000);
        // const song = document.querySelector('#song')
        // thumbnail = document.querySelector('#thumbnail');
        $("#play-pause").removeClass('fa-play').addClass('fa-pause');
        // thumbnail.style.transform = "scale(1.15)";
        
        song.play();
        playing = false;
    } else {
        clearInterval(reco_event)
        clearInterval(reco_summ)
        $("#play-pause").removeClass('fa-pause').addClass('fa-play');
        // thumbnail.style.transform = "scale(1)"
        
        song.pause();
        playing = true;
    }
}
function updateProgressValue() {
    progressBar.max = song.duration;
    progressBar.value = song.currentTime;
    $('#inside').css("width", String(Math.floor((progressBar.value/progressBar.max)*100)) + "%");
    // inside.style.width = String(Math.floor((progressBar.value/progressBar.max)*100)) + "%";

    document.querySelector('.currentTime').innerHTML = (formatTime(Math.floor(song.currentTime)));
    if (document.querySelector('.durationTime').innerHTML === "NaN:NaN") {
        document.querySelector('.durationTime').innerHTML = "0:00";
    } else {
        document.querySelector('.durationTime').innerHTML = (formatTime(Math.floor(song.duration)));
    }
};

function formatTime(seconds) {
    let min = Math.floor((seconds / 60));
    let sec = Math.floor(seconds - (min * 60));
    if (sec < 10){ 
        sec  = `0${sec}`;
    };
    return `${min}:${sec}`;
};

function updateSummary() {
  //     axios.get('http://localhost:5000/recommend_summary/'+window.location.pathname.split("/")[2]+'/'+song.currentTime+'/')
  // .then((res) => {
  //   console.log(res);

  //   $("#summary").text(res.data.result);

// });
};

$(document).ready(function() {
	$('.marquee1').css('visibility', 'hidden');
  
  // place this within dom ready function
  function showmarquee1() {     
  	$('.marquee1').css('visibility', 'visible');

 }
 progressBar.value = 0
 // use setTimeout() to execute
 setTimeout(showmarquee1, 13000)
 setInterval(updateProgressValue, 500);
 updateImage()
 // if($("#poster").attr("src")===null){
 //  setTimeout(showmarquee1, 13000)
 // }
});

    outside.addEventListener('click', function(e) {

      var pct = e.offsetX / outside.offsetWidth;
      progressBar.value=pct*song.duration
      song.currentTime = progressBar.value;
      $('#inside').css('width', e.offsetX + "px");
      // inside.style.width = e.offsetX + "px";
      changeProgressBar()
      // calculate the %
      
      // inside.innerHTML = pct + " %";
    }, false);
function updateImage() {

    axios.get('http://localhost:5000/recommend_image/'+window.location.pathname.split("/")[2]+'/'+progressBar.value+'/')
  .then((res) => {
    console.log(res);
    image_links=res;
    $("#image1").attr("src",res.data.result[0][1][0])
    $("#image2").attr("src",res.data.result[0][1][1])
    $("#image3").attr("src",res.data.result[0][1][2])
    $("#image4").attr("src",res.data.result[0][1][3])
    $("#image5").attr("src",res.data.result[1][1][0])
    $("#image6").attr("src",res.data.result[1][1][1])
    $("#image7").attr("src",res.data.result[1][1][2])
    $("#image8").attr("src",res.data.result[1][1][3])
    $("#image9").attr("src",res.data.result[2][1][0])
    $("#image10").attr("src",res.data.result[2][1][1])
    $("#image11").attr("src",res.data.result[2][1][2])
    $("#image12").attr("src",res.data.result[2][1][3])
    $("#image13").attr("src",res.data.result[3][1][0])
    $("#image14").attr("src",res.data.result[3][1][1])
    $("#image15").attr("src",res.data.result[3][1][2])
    $("#image16").attr("src",res.data.result[3][1][3])
    
});
};


function changeProgressBar() {
    
    axios.get('http://localhost:5000/recommend_image/'+window.location.pathname.split("/")[2]+'/'+song.currentTime+'/')
  .then((res) => {
    console.log(res);
    $("#image1").attr("src",res.data.result[0][1][0])
    $("#image2").attr("src",res.data.result[0][1][1])
    $("#image3").attr("src",res.data.result[0][1][2])
    $("#image4").attr("src",res.data.result[0][1][3])
    $("#image5").attr("src",res.data.result[1][1][0])
    $("#image6").attr("src",res.data.result[1][1][1])
    $("#image7").attr("src",res.data.result[1][1][2])
    $("#image8").attr("src",res.data.result[1][1][3])
    $("#image9").attr("src",res.data.result[2][1][0])
    $("#image10").attr("src",res.data.result[2][1][1])
    $("#image11").attr("src",res.data.result[2][1][2])
    $("#image12").attr("src",res.data.result[2][1][3])
    $("#image13").attr("src",res.data.result[3][1][0])
    $("#image14").attr("src",res.data.result[3][1][1])
    $("#image15").attr("src",res.data.result[3][1][2])
    $("#image16").attr("src",res.data.result[3][1][3])

});
//       axios.get('http://localhost:5000/recommend_summary/'+window.location.pathname.split("/")[2]+'/'+song.currentTime+'/')
//   .then((res) => {
//     console.log(res);

//     $("#summary").text(res.data.result);

// });
};
function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}
// document.addEventListener("DOMContentLoaded", function(event) {
//    document.querySelectorAll('img').forEach(function(img){
//     var count1=getRandomInt(4);
//     var count2=getRandomInt(4);
//     console.log(image_links)
//     img.onerror = function(){this.src=image_links.data.result[count1][1][count2]};
//    })
// });

$('img').on("error", function() {
  var count1=getRandomInt(4);
  var count2=getRandomInt(4);
  $(this).attr('src', image_links.data.result[count1][1][count2]);
});

$(".left-marquee").hover(function(){
    $(".left-marquee").css("animation-play-state","paused");
    },function(){
    $(".left-marquee").css("animation-play-state","running");
});
$(".right-marquee").hover(function(){
    $(".right-marquee").css("animation-play-state","paused");
    },function(){
    $(".right-marquee").css("animation-play-state","running");
});
