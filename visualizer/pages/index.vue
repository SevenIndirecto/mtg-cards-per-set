<template>
  <v-row justify="center" align="center">
    <v-col cols="12">
      <v-card class="py-4 d-flex">
        <v-card-text>
        Alpha: Modern Format only
        <br> Timespan: 2021-12-01 - 2022-01-31
        <br> Source: MTG Goldfish
        </v-card-text>
      </v-card>
      <v-card>
        <v-card-actions>
          <v-switch
            v-model="showAsImages"
            label="Show as images"
          ></v-switch>
        </v-card-actions>
        <v-card-title class="headline">
          <template v-if="activeSet">{{ activeSet.name }} ({{ activeSet.releaseDate }})</template>
        </v-card-title>
        <v-card-text>
          <v-autocomplete
            v-model="activeSetLabel"
            :items="setLabels"
            label="Select set"
            rounded
            solo
            auto-select-first
            @select="onSetSelected"
          ></v-autocomplete>

          <v-row v-if="showAsImages">
            <v-col
              v-for="card in cardsInSet"
              :key="card.name"
              class="d-flex child-flex"
              lg="3"
              md="4"
              sm="6"
              xs="6"
            >
              <v-card>
                <v-img
                  :src="scryfallImageUrl(card.scryfallId)"
                  :lazy-src="scryfallImageUrl(card.scryfallId)"
                  class="grey lighten-2"
                >
                  <template v-slot:placeholder>
                    <v-row
                      class="fill-height ma-0"
                      align="center"
                      justify="center"
                    >
                      <v-progress-circular
                        indeterminate
                        color="grey lighten-5"
                      ></v-progress-circular>
                    </v-row>
                  </template>
                </v-img>
                <v-card-title class="pa-0">
                  <span class="card-count">{{ card.count }}</span>
                </v-card-title>
              </v-card>

            </v-col>
          </v-row>
          <v-list v-else>
            <v-list-item
              v-for="card in cardsInSet"
              :key="card.name"
            >
              {{ card.name }} ({{ card.count }})
            </v-list-item>
          </v-list>

        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import sets_json from '~/output_data/sets.json';

export default {
  name: 'IndexPage',
  data() {
    return {
      key: '',
      activeSetLabel: null,
      cardsInSet: [],
      showAsImages: true,
    }
  },
  computed: {
    activeSet() {
      return this.sets[this.activeSetLabel] ?? null;
    },
    sets() {
      const setMap = {};
      for (let set of sets_json) {
        setMap[`${set.name} (${set.code})`] = set;
      }
      return setMap;
    },
    setLabels() {
      return sets_json.map(({ code, name }) => `${name} (${code})`);
    },
  },
  watch: {
    activeSetLabel(setLabel) {
      if (setLabel) {
        this.onSetSelected();
      }
    }
  },
  methods: {
    async onSetSelected() {
      let cards = [];
      try {
        cards = (await import(`~/output_data/sets/${this.activeSet.code}.json`)).default;
      } catch (e) {
        console.log(e);
      }
      this.cardsInSet = [...cards];
    },
    scryfallImageUrl(id) {
      return `https://c1.scryfall.com/file/scryfall-cards/large/front/${id[0]}/${id[1]}/${id}.jpg`;
    }
  },
}
</script>

<style scoped>
.card-count {
  font-size: 1rem;
  margin: 0 auto;
}
</style>
