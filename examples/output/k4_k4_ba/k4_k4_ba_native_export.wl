SetDirectory[DirectoryName[$InputFileName]];

hEdges = {1 \[UndirectedEdge] 2, 1 \[UndirectedEdge] 3, 1 \[UndirectedEdge] 4, 2 \[UndirectedEdge] 3, 2 \[UndirectedEdge] 4, 3 \[UndirectedEdge] 4, 5 \[UndirectedEdge] 6, 5 \[UndirectedEdge] 7, 5 \[UndirectedEdge] 8, 6 \[UndirectedEdge] 7, 6 \[UndirectedEdge] 8, 7 \[UndirectedEdge] 8};

gEdges = {1 \[UndirectedEdge] 2, 1 \[UndirectedEdge] 3, 1 \[UndirectedEdge] 4, 1 \[UndirectedEdge] 5, 1 \[UndirectedEdge] 6, 1 \[UndirectedEdge] 9, 1 \[UndirectedEdge] 10, 1 \[UndirectedEdge] 14, 1 \[UndirectedEdge] 22, 1 \[UndirectedEdge] 24, 1 \[UndirectedEdge] 28, 1 \[UndirectedEdge] 29, 1 \[UndirectedEdge] 30, 1 \[UndirectedEdge] 45, 1 \[UndirectedEdge] 46, 3 \[UndirectedEdge] 4, 4 \[UndirectedEdge] 5, 4 \[UndirectedEdge] 6, 4 \[UndirectedEdge] 8, 4 \[UndirectedEdge] 10, 4 \[UndirectedEdge] 11, 4 \[UndirectedEdge] 12, 4 \[UndirectedEdge] 13, 4 \[UndirectedEdge] 16, 4 \[UndirectedEdge] 18, 4 \[UndirectedEdge] 19, 4 \[UndirectedEdge] 21, 4 \[UndirectedEdge] 29, 4 \[UndirectedEdge] 34, 4 \[UndirectedEdge] 42, 4 \[UndirectedEdge] 45, 4 \[UndirectedEdge] 50, 5 \[UndirectedEdge] 7, 5 \[UndirectedEdge] 9, 5 \[UndirectedEdge] 11, 5 \[UndirectedEdge] 21, 5 \[UndirectedEdge] 23, 5 \[UndirectedEdge] 24, 5 \[UndirectedEdge] 33, 5 \[UndirectedEdge] 34, 5 \[UndirectedEdge] 35, 5 \[UndirectedEdge] 37, 5 \[UndirectedEdge] 39, 5 \[UndirectedEdge] 49, 6 \[UndirectedEdge] 7, 6 \[UndirectedEdge] 47, 7 \[UndirectedEdge] 8, 7 \[UndirectedEdge] 13, 7 \[UndirectedEdge] 15, 7 \[UndirectedEdge] 27, 7 \[UndirectedEdge] 31, 7 \[UndirectedEdge] 40, 8 \[UndirectedEdge] 17, 8 \[UndirectedEdge] 33, 8 \[UndirectedEdge] 40, 8 \[UndirectedEdge] 47, 8 \[UndirectedEdge] 48, 9 \[UndirectedEdge] 17, 9 \[UndirectedEdge] 19, 9 \[UndirectedEdge] 20, 9 \[UndirectedEdge] 35, 10 \[UndirectedEdge] 15, 10 \[UndirectedEdge] 26, 10 \[UndirectedEdge] 30, 10 \[UndirectedEdge] 37, 10 \[UndirectedEdge] 44, 11 \[UndirectedEdge] 12, 11 \[UndirectedEdge] 16, 11 \[UndirectedEdge] 38, 11 \[UndirectedEdge] 39, 12 \[UndirectedEdge] 18, 12 \[UndirectedEdge] 49, 13 \[UndirectedEdge] 14, 13 \[UndirectedEdge] 26, 13 \[UndirectedEdge] 27, 14 \[UndirectedEdge] 43, 14 \[UndirectedEdge] 44, 15 \[UndirectedEdge] 23, 15 \[UndirectedEdge] 41, 18 \[UndirectedEdge] 25, 19 \[UndirectedEdge] 20, 19 \[UndirectedEdge] 32, 19 \[UndirectedEdge] 46, 19 \[UndirectedEdge] 48, 20 \[UndirectedEdge] 22, 20 \[UndirectedEdge] 36, 21 \[UndirectedEdge] 36, 21 \[UndirectedEdge] 43, 22 \[UndirectedEdge] 25, 25 \[UndirectedEdge] 28, 27 \[UndirectedEdge] 41, 28 \[UndirectedEdge] 31, 28 \[UndirectedEdge] 32, 37 \[UndirectedEdge] 38, 39 \[UndirectedEdge] 42, 47 \[UndirectedEdge] 50};

vertexMapping = <|1 -> 4, 2 -> 1, 3 -> 7, 4 -> 6, 5 -> 5, 6 -> 10, 7 -> 9, 8 -> 11|>;

edgeMapping = <|1 -> {1 \[UndirectedEdge] 4}, 2 -> {4 \[UndirectedEdge] 8, 7 \[UndirectedEdge] 8}, 3 -> {4 \[UndirectedEdge] 6}, 4 -> {1 \[UndirectedEdge] 5, 5 \[UndirectedEdge] 7}, 5 -> {1 \[UndirectedEdge] 6}, 6 -> {6 \[UndirectedEdge] 7}, 7 -> {5 \[UndirectedEdge] 37, 10 \[UndirectedEdge] 37}, 8 -> {5 \[UndirectedEdge] 35, 9 \[UndirectedEdge] 35}, 9 -> {5 \[UndirectedEdge] 39, 11 \[UndirectedEdge] 39}, 10 -> {1 \[UndirectedEdge] 10, 1 \[UndirectedEdge] 9}, 11 -> {4 \[UndirectedEdge] 10, 4 \[UndirectedEdge] 11}, 12 -> {5 \[UndirectedEdge] 9, 5 \[UndirectedEdge] 11}|>;

edgeColorList = ColorData[97] /@ Range[Length[hEdges]];

hEdgeStyleRules = Thread[hEdges -> (Directive[#, AbsoluteThickness[3.2]] & /@ edgeColorList)];

edgeMappingFirst = AssociationThread[Range[1, 6], edgeMapping /@ Range[1, 6]];
edgeMappingSecond = AssociationThread[Range[7, 12], edgeMapping /@ Range[7, 12]];

gImmersedStyleRulesFirst = Flatten[
  Table[
    Thread[edgeMapping[i] -> Directive[edgeColorList[[i]], AbsoluteThickness[2.8]]],
    {i, 1, 6}
  ]
];

gImmersedStyleRulesSecond = Flatten[
  Table[
    Thread[edgeMapping[i] -> Directive[edgeColorList[[i]], AbsoluteThickness[2.8]]],
    {i, 7, 12}
  ]
];

gBackgroundStyleRules = Thread[
  EdgeList[Graph[Range[50], gEdges]] ->
    Directive[GrayLevel[0.72], Opacity[0.24], AbsoluteThickness[0.75]]
];

branchVertexStyleRulesFirst = Thread[Values[KeyTake[vertexMapping, Range[1, 4]]] -> Directive[Darker[Cyan, 0.35], PointSize[0.02]]];
branchVertexStyleRulesSecond = Thread[Values[KeyTake[vertexMapping, Range[5, 8]]] -> Directive[Darker[Orange, 0.15], PointSize[0.02]]];

hCoordinates = <|1 -> {-1.8, 0.65}, 2 -> {-0.95, 0.65}, 3 -> {-0.95, -0.2}, 4 -> {-1.8, -0.2}, 5 -> {0.95, 0.65}, 6 -> {1.8, 0.65}, 7 -> {1.8, -0.2}, 8 -> {0.95, -0.2}|>;

hPlot = Graph[
  Range[8],
  hEdges,
  VertexCoordinates -> Normal[hCoordinates],
  VertexLabels -> Placed["Name", Center],
  EdgeStyle -> hEdgeStyleRules,
  VertexSize -> 0.22,
  ImageSize -> 300,
  PlotLabel -> Style["H = K4 + K4", 14, FontFamily -> "Arial"]
];

gPlotFirst = Graph[
  Range[50],
  gEdges,
  GraphLayout -> "SpringElectricalEmbedding",
  VertexLabels -> None,
  EdgeStyle -> Join[gBackgroundStyleRules, gImmersedStyleRulesFirst],
  VertexStyle -> branchVertexStyleRulesFirst,
  VertexSize -> 0.12,
  ImageSize -> 430,
  PlotLabel -> Style["G with first K4 image, seed 0", 14, FontFamily -> "Arial"]
];

gPlotSecond = Graph[
  Range[50],
  gEdges,
  GraphLayout -> "SpringElectricalEmbedding",
  VertexLabels -> None,
  EdgeStyle -> Join[gBackgroundStyleRules, gImmersedStyleRulesSecond],
  VertexStyle -> branchVertexStyleRulesSecond,
  VertexSize -> 0.12,
  ImageSize -> 430,
  PlotLabel -> Style["G with second K4 image, seed 0", 14, FontFamily -> "Arial"]
];

mappingPanel = Pane[
  Framed[
    Column[{
      Style["Vertex mapping", Bold, 12, FontFamily -> "Arial"],
      vertexMapping,
      Spacer[8],
      Style["Edge mapping: colors match the two immersed K4 components", Bold, 12, FontFamily -> "Arial"],
      edgeMapping
    }, Spacings -> 0.7],
    FrameStyle -> GrayLevel[0.82],
    Background -> White,
    ImageMargins -> 4
  ],
  {860, 230},
  Scrollbars -> False
];

figure = Grid[
  {{hPlot, gPlotFirst, gPlotSecond}, {SpanFromLeft, mappingPanel, SpanFromLeft}},
  Spacings -> {1.2, 0.8},
  Alignment -> Center,
  Background -> White
];

Export["k4_k4_ba_native_colored.pdf", figure];
Export["k4_k4_ba_native_colored.png", figure, ImageResolution -> 300];
Export["k4_k4_ba_h_native_colored.pdf", hPlot];
Export["k4_k4_ba_g_first_native_colored.pdf", gPlotFirst];
Export["k4_k4_ba_g_second_native_colored.pdf", gPlotSecond];
Print["Exported native Mathematica colored figures."];
