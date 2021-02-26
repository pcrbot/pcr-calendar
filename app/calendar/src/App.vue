<template>
  <div id="app">
    <el-calendar v-loading="isLoading">
      <template slot="dateCell" slot-scope="{date,data}">
        <p>{{ data.day }}</p>
        <p>{{ campaign(date.toLocaleDateString()) }}</p>
      </template>
    </el-calendar>
  </div>
</template>

<script>
import axios from "axios";

function parseDate(datestring) {
  var [d, t] = datestring.split(" ");
  var [yy, mm, dd] = d.split("/");
  var hh = t.split(":")[0];
  if (hh < 5) {
    dd -= 1;
  }
  return new Date(yy, mm - 1, dd);
}

function parsecampaign(campaigns) {
  var timeline = [];
  for (const campaign of campaigns) {
    var campaigntime = parseDate(campaign.start_time);
    var end = parseDate(campaign.end_time);
    while (campaigntime <= end) {
      let d = campaigntime.toLocaleDateString();
      timeline[d]
        ? timeline[d].push(campaign.name)
        : (timeline[d] = [campaign.name]);
      campaigntime.setDate(campaigntime.getDate() + 1);
    }
  }
  return timeline;
}

export default {
  data: () => {
    return {
      isLoading: true,
      timeline: []
    };
  },
  methods: {
    campaign: function(day) {
      var cams = this.timeline[day];
      if (!cams) {
        return "";
      }
      return cams.join("\n");
    }
  },
  mounted: function() {
    var thisvue = this;
    var area = window.location.hash.substring(1);
    var apipath;
    if (area === "cn") {
      apipath = "https://pcrbot.github.io/calendar-updater-action/cn.json";
    } else if (area === "jp") {
      apipath = "https://pcrbot.github.io/calendar-updater-action/jp.json";
    } else if (area === "tw") {
      apipath = "https://pcrbot.github.io/calendar-updater-action/tw.json";
    } else {
      thisvue.$message({ type: "error", message: "此链接无效" });
      return;
    }
    axios
      .get(apipath)
      .then(function(res) {
        thisvue.timeline = parsecampaign(res.data);
        thisvue.isLoading = false;
      })
      .catch(function(error) {
        thisvue.$message({ type: "error", message: error });
        thisvue.isLoading = false;
      });
  }
};
</script>

<style>
.el-calendar-day {
  white-space: pre-wrap;
}
.el-calendar-table .el-calendar-day {
  height: auto;
}
</style>