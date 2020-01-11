<template>
    <div>
        <h1>Camera obscura</h1>
        <h3>{{ lightIntensity }} lux</h3>
    </div>  
</template>

<script>
import axios from 'axios';
import Crunker from 'crunker';
export default {
    name: 'CameraObscura',
    props: {
        msg: String
    },
    data: function() {
       return {
          lightIntensity: 0,
          audio: new Crunker({sampleRate: 48000}),
          buffers: null
        }
    },
    mounted: function () {
        this.audio.fetchAudio('sounds/single_click.wav', 'sounds/single_crackle_slower.wav', 'sounds/single_crackle_faster.wav', 'sounds/double_crackle.wav')
            .then(x => {
                this.buffers = x;
                // eslint-disable-next-line no-console
                console.log("Buffers:", this.buffers);
            });
        this.$nextTick(function () {
            window.setInterval(() => {
                // eslint-disable-next-line no-console
                console.log("Playing...");
                axios.get(`http://vitez.si:8086/query?pretty=true&db=ioi&q=SELECT%20Last(intensity)%20from%20lightIntensity`)
                .then(response => {
                    // JSON responses are automatically parsed.
                    var intensity = response.data.results[0].series[0].values[0][1];
                    // eslint-disable-next-line no-console
                    console.log(intensity);
                    this.lightIntensity = intensity;
                    var converted = this.convertToLogarithm(intensity);
                    var limits = this.generateLimits(converted);
                    this.createAndPlaySound(limits);
                })
                .catch(e => {
                    // eslint-disable-next-line no-console
                    console.log(e);
                })
            }, 2000);
        })
    },
    methods: {
        convertToLogarithm(value) {
            return Math.log10(value) * 100;
        },
        generateLimits(value) {
            var crackleLimit = 0;
            var upperSilenceLimit = 0;
            var lowerSilenceLimit = 0;
            if(value < 250) {
                crackleLimit = value / 20;
                upperSilenceLimit = 750 - value;
                lowerSilenceLimit = upperSilenceLimit / 3;
            } else if(value < 350) {
                crackleLimit = value / 15;
                upperSilenceLimit = 650 - value;
                lowerSilenceLimit = upperSilenceLimit / 4;
            } else if(value < 450) {
                crackleLimit = value / 10;
                upperSilenceLimit = 600 - value;
                lowerSilenceLimit = upperSilenceLimit / 5;
            } else {
                crackleLimit = value / 7;
                upperSilenceLimit = 550 - value;
                lowerSilenceLimit = upperSilenceLimit / 10;
            }
            if(crackleLimit == 0) {
                crackleLimit = 1;
            }
            return {crackle: crackleLimit, upper: upperSilenceLimit, lower: lowerSilenceLimit};
        },
        randomNumber(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        },
        silentBuffer(duration) {
            var createBuffer = require('audio-buffer-from');
            var buff = createBuffer(48*duration, {channels: 2, sampleRate: 48000});
            return buff;
        },
        createAndPlaySound(limits) {
            /*
            Buffers
            0 -> single_click
            1 -> single_crackle_slow
            2 -> single_crackle_fast
            3 -> double_crackle
            */
            var sound = this.silentBuffer(10);
            var sampleLength = 2000;
            var totalLength = 0;
            while(totalLength < sampleLength) {
                var silencePeriod = this.randomNumber(limits.lower, limits.upper);
                totalLength += silencePeriod;
                sound = this.audio.concatAudio([sound, this.silentBuffer(silencePeriod)]);
                if(this.randomNumber(1, 100) < limits.crackle) {
                    var crackleIndex = this.randomNumber(1, 3);
                    sound = this.audio.concatAudio([sound, this.buffers[crackleIndex]]);
                    totalLength += this.buffers[crackleIndex].duration * 1000;
                } else {
                    sound = this.audio.concatAudio([sound, this.buffers[0]]);
                    totalLength += this.buffers[0].duration * 1000;
                }
            }
            this.audio.play(sound);
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
