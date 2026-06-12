SetDirectory[DirectoryName[$InputFileName]];

hEdges = {1 \[UndirectedEdge] 2, 1 \[UndirectedEdge] 3, 1 \[UndirectedEdge] 4, 2 \[UndirectedEdge] 3, 2 \[UndirectedEdge] 4, 3 \[UndirectedEdge] 4, 5 \[UndirectedEdge] 6, 5 \[UndirectedEdge] 7, 6 \[UndirectedEdge] 7};

gEdges = {1 \[UndirectedEdge] 2, 1 \[UndirectedEdge] 3, 1 \[UndirectedEdge] 7, 1 \[UndirectedEdge] 10, 1 \[UndirectedEdge] 13, 1 \[UndirectedEdge] 14, 1 \[UndirectedEdge] 15, 1 \[UndirectedEdge] 17, 1 \[UndirectedEdge] 18, 1 \[UndirectedEdge] 20, 1 \[UndirectedEdge] 23, 1 \[UndirectedEdge] 29, 1 \[UndirectedEdge] 33, 1 \[UndirectedEdge] 65, 1 \[UndirectedEdge] 66, 1 \[UndirectedEdge] 95, 1 \[UndirectedEdge] 97, 2 \[UndirectedEdge] 4, 2 \[UndirectedEdge] 5, 2 \[UndirectedEdge] 8, 2 \[UndirectedEdge] 9, 2 \[UndirectedEdge] 34, 2 \[UndirectedEdge] 37, 2 \[UndirectedEdge] 39, 2 \[UndirectedEdge] 43, 2 \[UndirectedEdge] 53, 2 \[UndirectedEdge] 54, 2 \[UndirectedEdge] 61, 2 \[UndirectedEdge] 79, 2 \[UndirectedEdge] 100, 3 \[UndirectedEdge] 4, 3 \[UndirectedEdge] 6, 3 \[UndirectedEdge] 27, 3 \[UndirectedEdge] 36, 3 \[UndirectedEdge] 37, 3 \[UndirectedEdge] 40, 3 \[UndirectedEdge] 56, 3 \[UndirectedEdge] 60, 3 \[UndirectedEdge] 69, 3 \[UndirectedEdge] 75, 4 \[UndirectedEdge] 5, 4 \[UndirectedEdge] 6, 4 \[UndirectedEdge] 8, 4 \[UndirectedEdge] 9, 4 \[UndirectedEdge] 10, 4 \[UndirectedEdge] 11, 4 \[UndirectedEdge] 12, 4 \[UndirectedEdge] 15, 4 \[UndirectedEdge] 18, 4 \[UndirectedEdge] 28, 4 \[UndirectedEdge] 41, 4 \[UndirectedEdge] 50, 4 \[UndirectedEdge] 53, 4 \[UndirectedEdge] 55, 4 \[UndirectedEdge] 57, 4 \[UndirectedEdge] 59, 4 \[UndirectedEdge] 61, 4 \[UndirectedEdge] 63, 4 \[UndirectedEdge] 77, 4 \[UndirectedEdge] 85, 4 \[UndirectedEdge] 100, 5 \[UndirectedEdge] 22, 5 \[UndirectedEdge] 28, 5 \[UndirectedEdge] 29, 5 \[UndirectedEdge] 44, 5 \[UndirectedEdge] 54, 5 \[UndirectedEdge] 71, 5 \[UndirectedEdge] 87, 6 \[UndirectedEdge] 7, 6 \[UndirectedEdge] 13, 6 \[UndirectedEdge] 71, 6 \[UndirectedEdge] 92, 7 \[UndirectedEdge] 11, 7 \[UndirectedEdge] 12, 7 \[UndirectedEdge] 19, 7 \[UndirectedEdge] 21, 7 \[UndirectedEdge] 26, 7 \[UndirectedEdge] 32, 7 \[UndirectedEdge] 48, 7 \[UndirectedEdge] 50, 7 \[UndirectedEdge] 59, 7 \[UndirectedEdge] 65, 7 \[UndirectedEdge] 67, 7 \[UndirectedEdge] 70, 7 \[UndirectedEdge] 73, 7 \[UndirectedEdge] 87, 7 \[UndirectedEdge] 95, 8 \[UndirectedEdge] 25, 8 \[UndirectedEdge] 51, 8 \[UndirectedEdge] 85, 8 \[UndirectedEdge] 92, 9 \[UndirectedEdge] 64, 10 \[UndirectedEdge] 31, 10 \[UndirectedEdge] 38, 10 \[UndirectedEdge] 52, 10 \[UndirectedEdge] 70, 10 \[UndirectedEdge] 73, 12 \[UndirectedEdge] 14, 12 \[UndirectedEdge] 16, 12 \[UndirectedEdge] 20, 12 \[UndirectedEdge] 32, 12 \[UndirectedEdge] 33, 12 \[UndirectedEdge] 38, 12 \[UndirectedEdge] 39, 12 \[UndirectedEdge] 57, 12 \[UndirectedEdge] 60, 12 \[UndirectedEdge] 74, 12 \[UndirectedEdge] 76, 12 \[UndirectedEdge] 79, 12 \[UndirectedEdge] 90, 13 \[UndirectedEdge] 17, 13 \[UndirectedEdge] 35, 14 \[UndirectedEdge] 21, 14 \[UndirectedEdge] 26, 14 \[UndirectedEdge] 30, 14 \[UndirectedEdge] 78, 14 \[UndirectedEdge] 94, 15 \[UndirectedEdge] 16, 15 \[UndirectedEdge] 22, 16 \[UndirectedEdge] 24, 16 \[UndirectedEdge] 76, 16 \[UndirectedEdge] 88, 16 \[UndirectedEdge] 98, 17 \[UndirectedEdge] 19, 17 \[UndirectedEdge] 34, 17 \[UndirectedEdge] 41, 17 \[UndirectedEdge] 49, 17 \[UndirectedEdge] 75, 17 \[UndirectedEdge] 77, 17 \[UndirectedEdge] 80, 18 \[UndirectedEdge] 23, 18 \[UndirectedEdge] 31, 18 \[UndirectedEdge] 36, 18 \[UndirectedEdge] 45, 18 \[UndirectedEdge] 49, 18 \[UndirectedEdge] 52, 18 \[UndirectedEdge] 62, 18 \[UndirectedEdge] 84, 18 \[UndirectedEdge] 89, 19 \[UndirectedEdge] 24, 19 \[UndirectedEdge] 30, 19 \[UndirectedEdge] 80, 21 \[UndirectedEdge] 27, 23 \[UndirectedEdge] 25, 26 \[UndirectedEdge] 42, 26 \[UndirectedEdge] 83, 26 \[UndirectedEdge] 90, 27 \[UndirectedEdge] 66, 27 \[UndirectedEdge] 84, 28 \[UndirectedEdge] 42, 28 \[UndirectedEdge] 44, 28 \[UndirectedEdge] 64, 29 \[UndirectedEdge] 86, 29 \[UndirectedEdge] 93, 30 \[UndirectedEdge] 74, 31 \[UndirectedEdge] 82, 33 \[UndirectedEdge] 35, 33 \[UndirectedEdge] 46, 33 \[UndirectedEdge] 91, 34 \[UndirectedEdge] 40, 35 \[UndirectedEdge] 46, 35 \[UndirectedEdge] 72, 36 \[UndirectedEdge] 62, 36 \[UndirectedEdge] 68, 37 \[UndirectedEdge] 43, 37 \[UndirectedEdge] 51, 40 \[UndirectedEdge] 89, 41 \[UndirectedEdge] 45, 41 \[UndirectedEdge] 88, 43 \[UndirectedEdge] 58, 44 \[UndirectedEdge] 48, 45 \[UndirectedEdge] 47, 46 \[UndirectedEdge] 47, 46 \[UndirectedEdge] 55, 46 \[UndirectedEdge] 58, 46 \[UndirectedEdge] 81, 51 \[UndirectedEdge] 56, 53 \[UndirectedEdge] 83, 54 \[UndirectedEdge] 67, 54 \[UndirectedEdge] 81, 54 \[UndirectedEdge] 82, 57 \[UndirectedEdge] 72, 57 \[UndirectedEdge] 86, 58 \[UndirectedEdge] 78, 59 \[UndirectedEdge] 94, 61 \[UndirectedEdge] 63, 61 \[UndirectedEdge] 69, 61 \[UndirectedEdge] 93, 62 \[UndirectedEdge] 68, 65 \[UndirectedEdge] 96, 66 \[UndirectedEdge] 91, 73 \[UndirectedEdge] 96, 83 \[UndirectedEdge] 97, 87 \[UndirectedEdge] 99, 88 \[UndirectedEdge] 98, 95 \[UndirectedEdge] 99};

vertexMapping = <|1 -> 95, 2 -> 87, 3 -> 7, 4 -> 1, 5 -> 98, 6 -> 88, 7 -> 16|>;

edgeMapping = <|1 -> {87 \[UndirectedEdge] 99, 95 \[UndirectedEdge] 99}, 2 -> {7 \[UndirectedEdge] 95}, 3 -> {1 \[UndirectedEdge] 95}, 4 -> {7 \[UndirectedEdge] 87}, 5 -> {1 \[UndirectedEdge] 29, 5 \[UndirectedEdge] 29, 5 \[UndirectedEdge] 87}, 6 -> {1 \[UndirectedEdge] 7}, 7 -> {88 \[UndirectedEdge] 98}, 8 -> {16 \[UndirectedEdge] 98}, 9 -> {16 \[UndirectedEdge] 88}|>;

edgeColorList = Join[ColorData[97] /@ Range[1, 6], {Darker[Orange, 0.05], Orange, Lighter[Orange, 0.2]}];

hEdgeStyleRules = Thread[hEdges -> (Directive[#, AbsoluteThickness[3.2]] & /@ edgeColorList)];

gImmersedStyleRules = Flatten[
  Table[
    Thread[edgeMapping[i] -> Directive[edgeColorList[[i]], AbsoluteThickness[2.8]]],
    {i, Length[hEdges]}
  ]
];

gBackgroundStyleRules = Thread[
  Complement[EdgeList[Graph[Range[100], gEdges]], Flatten[Values[edgeMapping]]] ->
    Directive[GrayLevel[0.72], Opacity[0.22], AbsoluteThickness[0.7]]
];

branchVertexStyleRules = Thread[
  Values[vertexMapping] ->
    (Directive[#, PointSize[0.018]] & /@ Join[ConstantArray[Darker[Cyan, 0.35], 4], ConstantArray[Darker[Orange, 0.15], 3]])
];

hCoordinates = Association[
  Join[
    Thread[Range[1, 4] -> (({-1.25, 0} + #) & /@ (0.72 CirclePoints[4]))],
    Thread[Range[5, 7] -> (({1.25, 0} + #) & /@ (0.62 CirclePoints[3]))]
  ]
];

hPlot = Graph[
  Range[7],
  hEdges,
  VertexCoordinates -> Normal[hCoordinates],
  VertexLabels -> Placed["Name", Center],
  EdgeStyle -> hEdgeStyleRules,
  VertexSize -> 0.22,
  ImageSize -> 300,
  PlotLabel -> Style["H = K4 + C3", 14, FontFamily -> "Arial"]
];

gPlot = Graph[
  Range[100],
  gEdges,
  GraphLayout -> "SpringElectricalEmbedding",
  VertexLabels -> None,
  EdgeStyle -> Join[gBackgroundStyleRules, gImmersedStyleRules],
  VertexStyle -> branchVertexStyleRules,
  VertexSize -> 0.095,
  ImageSize -> 560,
  PlotLabel -> Style["G = BA(100, 2), seed 16", 14, FontFamily -> "Arial"]
];

mappingPanel = Pane[
  Framed[
    Column[{
      Style["Vertex mapping", Bold, 12, FontFamily -> "Arial"],
      vertexMapping,
      Spacer[8],
      Style["Edge mapping: colors match the immersed K4 and C3", Bold, 12, FontFamily -> "Arial"],
      edgeMapping
    }, Spacings -> 0.7],
    FrameStyle -> GrayLevel[0.82],
    Background -> White,
    ImageMargins -> 4
  ],
  {860, 210},
  Scrollbars -> False
];

figure = Grid[
  {{hPlot, gPlot}, {SpanFromLeft, mappingPanel}},
  Spacings -> {1.2, 0.8},
  Alignment -> Center,
  Background -> White
];

Export["k4_c3_ba100_native_colored.pdf", figure];
Export["k4_c3_ba100_native_colored.png", figure, ImageResolution -> 300];
Export["k4_c3_ba100_h_native_colored.pdf", hPlot];
Export["k4_c3_ba100_g_native_colored.pdf", gPlot];
Print["Exported native Mathematica colored figures."];
