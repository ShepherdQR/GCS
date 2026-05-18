23:56-00:16 =  20 min


测试ds开始时： 42,224,269 


# 我们要引入“行为模型”，即：在原始的模型文件中，增加“History”字段，用于记录该约束图的构建过程。
- 以约束图”triangle_003.txt“为例，为每个部分增加标签。例如：
  - “Rigid Sets”
  - “Geometries”
  - “Constraints”
  - “History”
- 其中“History”部分，记录了该约束图的构建过程，例如：
  - “Add Rigid Set RS0”
  - “Add Geometry G0”
  - “Add Constraint C0”
- 请定义我们的模型格式，更新系统架构设计中对应的设计；且将cpp系统中的文件读写更新为该格式。将”triangle_003.txt“升级为”triangle_003.json“
- 在可视化系统中，能够支持加载/保存我们的新格式（例如”triangle_003.json“文件）；
- 在可视化系统中，增加一个”历史重演“功能，能够显示出约束图的构建过程。







