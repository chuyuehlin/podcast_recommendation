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
// progressBar.value is audio.currentTime
const outside = document.getElementById('outside');
const inside = document.getElementById('inside');
let pPause = document.querySelector('#play-pause'); // element where play and pause image appears
let caption_all = {};
let currentImageKeyword = "";
let playing = true;
let reco_event;
let reco_summ;
let reco_loadCap, reco_updateCap;
var service_url = 'https://kgsearch.googleapis.com/v1/entities:search';

function playPause() {
    if (playing) {
        updateImage();
        updateSummary();
        reco_event = setInterval(updateImage, 15000);
        reco_summ = setInterval(updateSummary, 5000);
        reco_loadCap = setInterval(function(){loadCaption("next")}, 50000);
        reco_updateCap = setInterval(updateCaption, 100);
        // const song = document.querySelector('#song')
        // thumbnail = document.querySelector('#thumbnail');
        $("#play-pause").removeClass('fa-play-circle').addClass('fa-pause-circle');
        // thumbnail.style.transform = "scale(1.15)";
        
        song.play();
        playing = false;
    } else {
        clearInterval(reco_event)
        clearInterval(reco_summ)
        clearInterval(reco_loadCap)
        clearInterval(reco_updateCap)
        $("#play-pause").removeClass('fa-pause-circle').addClass('fa-play-circle');
        // thumbnail.style.transform = "scale(1)"
        
        song.pause();
        playing = true;
    }
}

function updateProgressValue() {
    progressBar.max = song.duration;
    progressBar.value = song.currentTime;
    // $('#inside').css("width", String(Math.floor((progressBar.value/progressBar.max)*100)) + "%");
    // inside.style.width = String(Math.floor((progressBar.value/progressBar.max)*100)) + "%";
    $('#pgbar').val(Math.floor((progressBar.value/progressBar.max)*100));
    $('#pgbar').css("--val", Math.floor((progressBar.value/progressBar.max)*100));
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

function loadCaption(time) {
  console.log(time + " load " + song.currentTime);
  
  if(time == "next"){
    axios.get('http://localhost:5000/episode/' + window.location.pathname.split("/")[2] + "/caption/" + Math.round(song.currentTime/60)).then((res) => {
        console.log(res.data);
        caption_all = {...caption_all, ...res.data};
    });
  } else if (time == "now") {
    axios.get('http://localhost:5000/episode/' + window.location.pathname.split("/")[2] + "/caption/" + Math.floor(song.currentTime/60)).then((res) => {
        console.log(res.data);
        caption_all = {...caption_all, ...res.data};
    });
  }
}

function updateCaption() {
  let time = (Math.round(song.currentTime*10)/10).toFixed(3);
  if(time == Math.floor(time)) time = Math.floor(time);
  // document.getElementById("currenttime").innerHTML = time;

  if(caption_all[time] != null) {
    // find all match keyword
    let captionHTML = createCaptionHTML(caption_all[time]);
    // update caption
    document.getElementById("caption").innerHTML = captionHTML;
  }
}

function createCaptionHTML(captionHTML) {
  if(captionHTML == null) return null;

  let lowerCaption = captionHTML.toLowerCase();
  let pos = lowerCaption.indexOf(currentImageKeyword);
  
  while(pos != -1){
    console.log("MATCH! "+currentImageKeyword);
    let keywordLength = currentImageKeyword.length;
    
    captionHTML = captionHTML.slice(0, pos) 
                + "<span style='color:#da3c36'>"
                + captionHTML.slice(pos, pos+keywordLength) 
                + "</span>"
                + captionHTML.slice(pos+keywordLength);
    
    lowerCaption = captionHTML.toLowerCase();
    // 35 is length of "<span>...</span>"
    pos = lowerCaption.indexOf(currentImageKeyword, pos+35);
  }

  return captionHTML;
}

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
  
  $(function () {
    $('[data-toggle="tooltip"]').tooltip({
      animated: 'fade',
      placement: 'top',
      html: true
    });
  })
 
  progressBar.value = 0;
  // use setTimeout() to execute
  // if($("#poster").attr("src")===null){
  setTimeout(showmarquee1, 19000);
  setInterval(updateProgressValue, 500);
  updateImage();
  loadCaption("now");
  updateCaption();
  //  setTimeout(showmarquee1, 13000)
  // }
});

outside.addEventListener('click', function(e) {
    var pct = e.offsetX / outside.offsetWidth;
    progressBar.value=pct*song.duration
    song.currentTime = progressBar.value;
    // $('#inside').css('width', e.offsetX + "px");
    // inside.style.width = e.offsetX + "px";
    changeProgressBar();
    loadCaption();
    // calculate the %  
    // inside.innerHTML = pct + " %";
  }, false);

function updateImage() {
  axios.get('http://localhost:5000/recommend_image/'+window.location.pathname.split("/")[2]+'/'+progressBar.value+'/')
  .then((res) => {
    console.log(res);
    image_links=res;
    // tags_generator.inputs=[]
    // tags_generator.exist_key=[]
    tags_generator.growup()
    tags_generator.addInput([image_links.data.result[image_links.data.result.length-4][0],"",undefined,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
    $.each(image_links.data.result.slice(0,-4), function(t, item){
      var params = {
        'query': item[0],
        'limit': 1,
        'indent': true,
        'key' : 'AIzaSyB5UtPW_MpxtKb6HwF9cxDxEUflDqX4Wyk',
      };
      // tags_generator.removeIfMax()
      $.getJSON(service_url + '?callback=?', params, function(response) {
        // tags_generator.addInput([item[0],"",undefined,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
        if(0 || response.itemListElement.length == 0 || ((parseInt(response.itemListElement[0]['resultScore'],10)<10000)&&(response.itemListElement[0]['result']['name'].toLowerCase()!=item[0].toLowerCase()))){
          // console.log("OKOK")  
          tags_generator.addInput([item[0],"",undefined,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
        } else {
          $.each(response.itemListElement, function(i, element) {
            var name = element['result']['name'];
            var des = "";
            var url = "";
            if(typeof element['result']['description'] === 'undefined') {
              des = element['result']['detailedDescription']['articleBody'];
            } else {
              des = element['result']['description'];
            }
            url = element['result']['url'];
            tags_generator.addInput([item[0],"["+name+"]"+des,url,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
            $(function () {
              $('[data-toggle="tooltip"]').tooltip({
                animated: 'fade',
                placement: 'top',
                html: true
              });
            });
          });
        }
      });
    });
    // tags_generator.removeIfMax()

    $(function () {
      $('[data-toggle="tooltip"]').tooltip({
        animated: 'fade',
        placement: 'top',
        html: true
        });
    });

    $("#image1").attr("src",image_links.data.result[0][1][0]).attr("title",image_links.data.result[0][0])
    $("#image2").attr("src",image_links.data.result[1][1][0]).attr("title",image_links.data.result[1][0])
    $("#image3").attr("src",image_links.data.result[2][1][0]).attr("title",image_links.data.result[2][0])
    $("#image4").attr("src",image_links.data.result[3][1][0]).attr("title",image_links.data.result[3][0])
    $("#image5").attr("src",image_links.data.result[0][1][1]).attr("title",image_links.data.result[0][0])
    $("#image6").attr("src",image_links.data.result[1][1][1]).attr("title",image_links.data.result[1][0])
    $("#image7").attr("src",image_links.data.result[2][1][1]).attr("title",image_links.data.result[2][0])
    $("#image8").attr("src",image_links.data.result[3][1][1]).attr("title",image_links.data.result[3][0])
    $("#image9").attr("src",image_links.data.result[0][1][2]).attr("title",image_links.data.result[0][0])
    $("#image10").attr("src",image_links.data.result[1][1][2]).attr("title",image_links.data.result[1][0])
    $("#image11").attr("src",image_links.data.result[2][1][2]).attr("title",image_links.data.result[2][0])
    $("#image12").attr("src",image_links.data.result[3][1][2]).attr("title",image_links.data.result[3][0])
    $("#image13").attr("src",image_links.data.result[0][1][3]).attr("title",image_links.data.result[0][0])
    $("#image14").attr("src",image_links.data.result[1][1][3]).attr("title",image_links.data.result[1][0])
    $("#image15").attr("src",image_links.data.result[2][1][3]).attr("title",image_links.data.result[2][0])
    $("#image16").attr("src",image_links.data.result[3][1][3]).attr("title",image_links.data.result[3][0]) 
  });
};


function changeProgressBar() {
  axios.get('http://localhost:5000/recommend_image/'+window.location.pathname.split("/")[2]+'/'+song.currentTime+'/')
  .then((res) => {
    console.log(res);
    image_links=res;
    // tags_generator.inputs=[]
    // tags_generator.exist_key=[]
    tags_generator.growup()
    tags_generator.addInput([image_links.data.result[image_links.data.result.length-4][0],"",undefined,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
    $.each(image_links.data.result.slice(0,-4), function(t, item){ //.slice(0,-4)   
      var params = {
        'query': item[0],
        'limit': 1,
        'indent': true,
        'key' : 'AIzaSyB5UtPW_MpxtKb6HwF9cxDxEUflDqX4Wyk',
      };
      // tags_generator.removeIfMax()
      $.getJSON(service_url + '?callback=?', params, function(response) {
        if(response.itemListElement.length==0||((parseInt(response.itemListElement[0]['resultScore'],10)<10000)&&(response.itemListElement[0]['result']['name'].toLowerCase()!=item[0].toLowerCase()))){
          tags_generator.addInput([item[0],"",undefined,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
        } else {
          $.each(response.itemListElement, function(i, element) {
            var name=element['result']['name']
            var des=""
            var url=""
            if(typeof element['result']['description'] === 'undefined') {
              des=element['result']['detailedDescription']['articleBody']
            } else {
              des=element['result']['description']
            }
            url=element['result']['url']
            tags_generator.addInput([item[0],"["+name+"]"+des,url,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
            $(function () {
              $('[data-toggle="tooltip"]').tooltip({
                animated: 'fade',
                placement: 'top',
                html: true
              })
            })
          });
        }
      });
    });
    
    // tags_generator.removeTags();
    // tags_generator.removeTags();
    // tags_generator.removeTags();
    // tags_generator.removeTags();
    // tags_generator.addInput([res.data.result[0][0],res.data.result[0][0]]);
    // tags_generator.addInput([res.data.result[1][0],res.data.result[1][0]]);
    // tags_generator.addInput([res.data.result[2][0],res.data.result[2][0]]);
    // tags_generator.addInput([res.data.result[3][0],res.data.result[3][0]]);
    // tags_generator.removeIfMax()
    
    $(function () {
      $('[data-toggle="tooltip"]').tooltip({
        animated: 'fade',
        placement: 'top',
        html: true
      });
    });

    $("#image1").attr("src",image_links.data.result[0][1][0]).attr("title",image_links.data.result[0][0])
    $("#image2").attr("src",image_links.data.result[1][1][0]).attr("title",image_links.data.result[1][0])
    $("#image3").attr("src",image_links.data.result[2][1][0]).attr("title",image_links.data.result[2][0])
    $("#image4").attr("src",image_links.data.result[3][1][0]).attr("title",image_links.data.result[3][0])
    $("#image5").attr("src",image_links.data.result[0][1][1]).attr("title",image_links.data.result[0][0])
    $("#image6").attr("src",image_links.data.result[1][1][1]).attr("title",image_links.data.result[1][0])
    $("#image7").attr("src",image_links.data.result[2][1][1]).attr("title",image_links.data.result[2][0])
    $("#image8").attr("src",image_links.data.result[3][1][1]).attr("title",image_links.data.result[3][0])
    $("#image9").attr("src",image_links.data.result[0][1][2]).attr("title",image_links.data.result[0][0])
    $("#image10").attr("src",image_links.data.result[1][1][2]).attr("title",image_links.data.result[1][0])
    $("#image11").attr("src",image_links.data.result[2][1][2]).attr("title",image_links.data.result[2][0])
    $("#image12").attr("src",image_links.data.result[3][1][2]).attr("title",image_links.data.result[3][0])
    $("#image13").attr("src",image_links.data.result[0][1][3]).attr("title",image_links.data.result[0][0])
    $("#image14").attr("src",image_links.data.result[1][1][3]).attr("title",image_links.data.result[1][0])
    $("#image15").attr("src",image_links.data.result[2][1][3]).attr("title",image_links.data.result[2][0])
    $("#image16").attr("src",image_links.data.result[3][1][3]).attr("title",image_links.data.result[3][0]) 
  });
//   axios.get('http://localhost:5000/recommend_summary/'+window.location.pathname.split("/")[2]+'/'+song.currentTime+'/')
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


var tags_generator = new Vue({
  delimiters: ['%%%', '%%%'],
  el: '#kw-vue',
  name: 'Adding kw-tags',
  data() {
    return {
      inputs: [],
      exist_key: [],
      age: []
    }
  },
  methods: {
    addInput(e) {
      if(!(this.exist_key.includes(e[0]))){
        this.age.push(1)
        this.inputs.push(e)
        this.exist_key.push(e[0])
      }else{
	let duindex = this.exist_key.indexOf(e[0])
	this.inputs.splice(duindex,1)
	this.exist_key.splice(duindex,1)
	this.age.splice(duindex,1)	
	this.addInput(e)
	}
    },
    removeTags(){
        this.inputs.shift()
        this.exist_key.shift()
        this.age.shift()
    },
    growup(){
        this.age.forEach(function(item, index, array){
          array[index] = item + 1;
        });
    },
    // removeIfMax(){
    //     while(this.exist_key.join('').length>85){
    //         this.removeTags()
    //     }
    // }
  },
  computed: {
    buttonText() {
      return this.showInput ? 'Hide input' : 'Show input'
    }
  },
  watch: {
    exist_key(){
        while(this.exist_key.join('').length>250){
            this.removeTags()
        }
    },
    age(){
        var that=this.inputs
        this.age.forEach(function(item, index, array){
          if(item==2){
            //round2
            // console.log("2")
            that[index][3]="btn btn-success btn-xs kw-tag list-complete-item tag-style2"
          }else if(item>=3){
            //round3
            // console.log("3")
            that[index][3]="btn btn-success btn-xs kw-tag list-complete-item tag-style3"
          }
        });
    }
  }

})

function showIframe() {
  /* Parent element */
  var widget = document.createElement("div");
  widget.style.position="fixed";
  widget.style.top="100px";
  widget.style.left="100px";
  widget.style.width="800px";
  widget.style.height="600px";

  /* picture uploading page frame */
  var iframe = document.createElement("iframe");
  iframe.src = "https://www.itread01.com/content/1542414730.html"; // use your picture upload URL here

  /* Add to document */
  widget.appendChild(iframe);
  document.body.appendChild(widget);
}

$('.slideshow').each(function () {

  let slideImgs = $(this).find('img');
  let slideImgsCount = slideImgs.length;
  let currentIndex = 0;

  slideImgs.eq(currentIndex).fadeIn();

  setInterval(showNextSlide, 5000);

  function showNextSlide() {
    let nextIndex = (currentIndex + 1) % slideImgsCount;
    $(".background-image").fadeOut();
    slideImgs.eq(currentIndex).fadeOut(600);
    
    $('.background-image').css("background-image", "url('"+slideImgs.eq(nextIndex).attr('src')+"')");
    
    currentImageKeyword = slideImgs.eq(nextIndex).attr("title");
    document.getElementById("currentKeyword").innerHTML = currentImageKeyword;

    $('.background-image').fadeIn();
    slideImgs.eq(nextIndex).fadeIn();
    currentIndex = nextIndex;

    // find all match keyword in caption
    let captionHTML = createCaptionHTML(document.getElementById("caption").innerHTML);
    // replace caption
    document.getElementById("caption").innerHTML = captionHTML;
  }
})



// 拉音樂框框
const _R = document.querySelector('[type=range]');

document.documentElement.classList.add('js');

_R.addEventListener('input', e => {
  _R.style.setProperty('--val', +_R.value);
}, false);
