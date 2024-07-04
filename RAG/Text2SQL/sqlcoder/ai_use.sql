/*
 Navicat Premium Data Transfer

 Source Server         : Kemove
 Source Server Type    : MySQL
 Source Server Version : 80037
 Source Host           : 192.168.100.111:3306
 Source Schema         : ai_use

 Target Server Type    : MySQL
 Target Server Version : 80037
 File Encoding         : 65001

 Date: 04/07/2024 15:12:01
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for dw_s_employment
-- ----------------------------
DROP TABLE IF EXISTS `dw_s_employment`;
CREATE TABLE `dw_s_employment`  (
  `xxdm` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校代码',
  `xxid` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校ID',
  `xxmc` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校名称',
  `xxsf` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校省份',
  `xxcs` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校城市',
  `bxcc` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '办学层次',
  `xxcc` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校层次',
  `xxlx` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校类型',
  `jb` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '届别',
  `yx` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '院系',
  `zydm` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '专业代码',
  `zy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '专业',
  `xkml` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学科门类',
  `zydl` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '专业大类',
  `zyfx` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '专业方向',
  `bj` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '班级',
  `xm` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '姓名',
  `xh` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学号',
  `sfzhm` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '身份证号码',
  `xl` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学历',
  `xb` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '性别',
  `sfslb` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '师范生类别',
  `jyknlb` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '困难生类别',
  `mz` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '民族',
  `kslb` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '城乡生源',
  `syszddm` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '生源所在地代码',
  `xl_c` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学历_合并',
  `sfslb_c` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '师范生类别_合并',
  `jyknlb_c` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '困难生类别_合并',
  `ssmz` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否少数民族',
  `ssmz_01` int NULL DEFAULT NULL COMMENT '少数民族人数',
  `syjjq` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '生源经济区',
  `sysf` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '生源省份',
  `sycs` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '生源城市',
  `bzr` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '班主任/辅导员',
  `lsbyqx` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否落实毕业去向',
  `lsbyqx_01` int NULL DEFAULT NULL COMMENT '落实毕业去向人数',
  `byqx1` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '毕业去向一级分类',
  `byqx2` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '毕业去向二级分类',
  `byqx3` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '毕业去向三级分类',
  `byqxdm` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '毕业去向代码',
  `byqx` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '毕业去向',
  `dwjy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否单位就业',
  `dwjy_01` int NULL DEFAULT NULL COMMENT '单位就业人数',
  `zzcy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否自主创业',
  `zzcy_01` int NULL DEFAULT NULL COMMENT '自主创业人数',
  `zyzy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否自由职业',
  `zyzy_01` int NULL DEFAULT NULL COMMENT '自由职业人数',
  `jnsx` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否境内升学',
  `jnsx_01` int NULL DEFAULT NULL COMMENT '境内升学人数',
  `jwlx` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否境外留学',
  `jwlx_01` int NULL DEFAULT NULL COMMENT '境外留学人数',
  `sx_01` int NULL DEFAULT NULL COMMENT '升学人数',
  `djy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否待就业',
  `djy_01` int NULL DEFAULT NULL COMMENT '待就业人数',
  `zbjy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否暂不就业',
  `zbjy_01` int NULL DEFAULT NULL COMMENT '暂不就业人数',
  `lhjy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否灵活就业',
  `lhjy_01` int NULL DEFAULT NULL COMMENT '灵活就业人数',
  `lhjylb` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL COMMENT '灵活就业类别',
  `dwmc` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL COMMENT '单位名称',
  `dwszddm` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '单位所在地代码',
  `dwzzjg` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '统一社会信用代码/组织机构代码',
  `dwhy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '单位行业',
  `dwxz` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '单位性质',
  `gzzwlb` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '工作职位类别',
  `sfmc` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '就业省份',
  `sqmc` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '就业城市',
  `qxmc` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '就业区县',
  `gxsjy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否高校所在省就业',
  `gxsjy_01` int NULL DEFAULT NULL COMMENT '高校所在省就业人数',
  `bshjy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否高校所在省会就业',
  `bshjy_01` int NULL DEFAULT NULL COMMENT '高校所在省会就业人数',
  `bcsjy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否高校所在城市就业',
  `bcsjy_01` int NULL DEFAULT NULL COMMENT '高校所在城市就业人数',
  `sysjy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否生源省就业',
  `sysjy_01` int NULL DEFAULT NULL COMMENT '生源省就业人数',
  `jcjy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '是否基层就业',
  `jcjy_01` int NULL DEFAULT NULL COMMENT '基层就业人数',
  `yxid` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '院系ID',
  `id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL COMMENT '主键ID',
  `xysh` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学院审核_生源',
  `xxsh` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校审核_生源',
  `xysh_jy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学院审核_就业',
  `xxsh_jy` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '学校审核_就业',
  `zrs` int NULL DEFAULT NULL COMMENT '总人数',
  `sxgxbq` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '境内升学高校层次标签',
  `sxgxlx` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '境内升学高校学校类型',
  `gj` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT '境外留学国家',
  `qs` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT 'QS排名_区间',
  `qs_c` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NULL DEFAULT NULL COMMENT 'QS排名_自定义的区间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `xxdm_idx`(`xxdm` ASC) USING BTREE,
  INDEX `xxid_idx`(`xxid` ASC) USING BTREE,
  INDEX `xxmc_idx`(`xxmc` ASC) USING BTREE,
  INDEX `xxsf_idx`(`xxsf` ASC) USING BTREE,
  INDEX `xb_idx`(`xb` ASC) USING BTREE,
  INDEX `mz_idx`(`mz` ASC) USING BTREE,
  INDEX `yxid_idx`(`yxid` ASC) USING BTREE,
  INDEX `xxcc_idx`(`xxcc` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_bin ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
