<template>
    <div>
        <h1>Camera obscura</h1>
        <h3>{{ lightIntensity }} lux</h3>
    </div>  
</template>

<script>
import axios from 'axios';
export default {
    name: 'CameraObscura',
    props: {
        msg: String
    },
    data: function() {
       return {
          lightIntensity: 0,
        }
    },
    mounted: function () {
        this.$nextTick(function () {
            window.setInterval(() => {
                // eslint-disable-next-line no-console
                console.log("Playing...");
                axios.get(`http://vitez.si:8086/query?pretty=true&db=ioi&q=SELECT%20Last(intensity)%20from%20lightIntensity`)
                .then(response => {
                    // JSON responses are automatically parsed.
                    // eslint-disable-next-line no-console
                    console.log(response);
                    var intensity = response.data.results[0].series[0].values[0][1];
                    // eslint-disable-next-line no-console
                    console.log(intensity);
                    this.lightIntensity = intensity;
                    this.playSound(intensity);
                })
                .catch(e => {
                    // eslint-disable-next-line no-console
                    console.log(e);
                })
            },2000);
        })
    },
    methods: {
        playSound(value) {
            if(value < 100) {
                this.playFile("sounds/low.mp3");
            } else if(value < 1000) {
                this.playFile("sounds/med.mp3");
            } else {
                this.playFile("sounds/high.mp3");
            }
        },
        playFile (file) {
            if(file) {
                var audio = new Audio(file);
                audio.play();
            }
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
