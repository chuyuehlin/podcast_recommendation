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
var service_url = 'https://kgsearch.googleapis.com/v1/entities:search';

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
         $(function () {
  $('[data-toggle="tooltip"]').tooltip({
    animated: 'fade',
    placement: 'top',
    html: true
    })
})
 progressBar.value = 0
 // use setTimeout() to execute
 setTimeout(showmarquee1, 19000)
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
    // tags_generator.inputs=[]
    // tags_generator.exist_key=[]
    tags_generator.growup()
    $.each(res.data.result.slice(0,-4), function(t, item){ //.slice(0,-4)
            
        var params = {
        'query': item[0],
        'limit': 1,
        'indent': true,
        'key' : 'AIzaSyB5UtPW_MpxtKb6HwF9cxDxEUflDqX4Wyk',
      };
      // tags_generator.removeIfMax()
          $.getJSON(service_url + '?callback=?', params, function(response) {
            if(0||response.itemListElement.length==0||((parseInt(response.itemListElement[0]['resultScore'],10)<10000)&&(response.itemListElement[0]['result']['name'].toLowerCase()!=item[0].toLowerCase()))){
                tags_generator.addInput([item[0],"",undefined,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
            }else{
            $.each(response.itemListElement, function(i, element) {
                        var name=element['result']['name']
                        var des=""
                        var url=""
                        if(typeof element['result']['description'] === 'undefined') {
                            des=element['result']['detailedDescription']['articleBody']
                        }
                        else {
                            des=element['result']['description']
                        }
                        url=element['result']['url']
                        tags_generator.addInput([name,des,url,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
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
    // tags_generator.removeIfMax()
    $(function () {
      $('[data-toggle="tooltip"]').tooltip({
        animated: 'fade',
        placement: 'top',
        html: true
        })
    })
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
    image_links=res;
    // tags_generator.inputs=[]
    // tags_generator.exist_key=[]
    tags_generator.growup()
    $.each(res.data.result.slice(0,-4), function(t, item){ //.slice(0,-4)
            
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
            }else{
            $.each(response.itemListElement, function(i, element) {
                        var name=element['result']['name']
                        var des=""
                        var url=""
                        if(typeof element['result']['description'] === 'undefined') {
                            des=element['result']['detailedDescription']['articleBody']
                        }
                        else {
                            des=element['result']['description']
                        }
                        url=element['result']['url']
                        tags_generator.addInput([name,des,url,"btn btn-success btn-xs kw-tag list-complete-item tag-style1"]);
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
        })
    })
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


var tags_generator = new Vue({
  delimiters: ['%%%', '%%%'],
  el: '#kw-vue',
  name: 'Adding kw-tags',
  data() {
    return {
      inputs: [],
      exist_key: [],
      age: [],
    }
  },
  methods: {
    addInput(e) {
    if(!(this.exist_key.includes(e[0]))){
      this.age.push(1)
      this.inputs.push(e)
      this.exist_key.push(e[0])
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
    }
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
        while(this.exist_key.join('').length>175){
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
