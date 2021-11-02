Vue.use(VueInstantSearch);

var app = new Vue({
    el: '#app',
    data: {
        searchClient: instantMeiliSearch(
            'http://localhost:7700',
            ''
        ),
        title: "PodReSystem",
        firstclick: false,
        moveSearchBar: false,
        moveTitle: false,
        displayHits: false,
        preview: false,
        previewURI: null
    },
    watch: {
        firstclick: function(val) {
            if(this.firstclick){
                this.title = "PRSystem";
                this.moveSearchBar = true;
                this.moveTitle = true;
                this.displayHits = true;
            }
        },
        previewURI: function(val) {
             if(this.preview) this.preview = false;
             else this.preview = true;
        }
    }
});
