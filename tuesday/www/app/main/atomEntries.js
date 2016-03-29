app.controller('AtomEntryController', function ($scope, filterFilter) {
    $scope.filtered = $scope.model = []
    $scope.columns = [
        { 'name': 'score', 'title': 'Score', 'show': true, 'type': 'float' },
        { 'name': 'distance', 'title': 'Match', 'show': true, 'type': 'float' },
        { 'name': 'title', 'title': 'Title', 'show': true, 'type': 'string' },
        { 'name': 'summary', 'title': 'Description', 'show': true, 'type': 'string' },
        { 'name': 'author', 'title': 'Author(s)', 'show': true, 'type': 'string' },
        { 'name': 'updated', 'title': 'Scanned', 'show': true, 'type': 'date' },
        { 'name': 'source', 'title': 'Source', 'show': false, 'type': 'string' },
        { 'name': 'token', 'title': 'Token', 'show': true, 'type': 'string' },
        { 'name': 'lemma', 'title': 'Lemma', 'show': true, 'type': 'string' },
        { 'name': 'stem', 'title': 'Stem', 'show': true, 'type': 'string' },
        { 'name': 'pos', 'title': 'Part of Speech', 'show': true, 'type': 'string' },
        { 'name': 'morph', 'title': 'Morphology', 'show': true, 'type': 'string' },
        { 'name': 'morph_id', 'title': 'Morphology', 'show': true, 'type': 'int' },
        { 'name': 'syntax', 'title': 'Syntax', 'show': true, 'type': 'string' },
        { 'name': 'syntax_id', 'title': 'Syntax', 'show': true, 'type': 'int' }
    ]

    $scope.loading = true;

    /************************************************************************************************
    * Data Model Methods
    */

    $scope.onModelLoaded = function (data) {
        $scope.model = data;
        if ($scope.model == null) {
            $scope.model = [];
            return;
        }

        if ($scope.model.length > 0) {
            $scope.loading = false;
        }

        // Reset the columns
        angular.forEach($scope.columns, function (column) {
            column.show = false;
        });

        // Initialize the columns
        angular.forEach($scope.model, function (row) {
            angular.forEach($scope.columns, function (column) {
                cell = row[column.name]
                if (cell !== undefined) {
                    column.show = true;
                }
            });

            // Fix up the 'updated' column
            if ("updated" in row) {
                row["updated"] = new Date(row["updated"]).toLocaleString();
            }

            if ("links" in row) {
                // Pop the 'View/Edit' link as the primary
                var elem = row["links"].shift();
                row["view"] = elem.href.replace('/api/v1/', '/');

                // Fix the urls
                angular.forEach(row["links"], function (link) {
                    link.href = link.href.replace('/api/v1/', '/');
                });
            }
        });

        angular.forEach($scope.columns, function (column) {
            if ($scope.orderBy == undefined && column.show) {
                if (column.name == 'score' || column.name == 'distance')
                    $scope.orderBy = '-' + column.name;
                else
                    $scope.orderBy = column.name;
            }
        });

        $scope.showNavigation = ($scope.model.length > 20);

        // Initialize the pagination data
        $scope.applyFilter();
    }

    /************************************************************************************************
     * Table Members
     */

    $scope.searchText = '';

    $scope.totalItems = 0;
    $scope.pageSize = 20
    $scope.currentPage = 1;
    $scope.offset = 0;
    $scope.lastShown = 0;

    $scope.applyFilter = function () {
        // Create $scope.filtered and then calculate $scope.totalItems, no racing!
        var a = $scope.filterText($scope.model);

        $scope.filtered = a;
        $scope.totalItems = $scope.filtered.length;
        $scope.currentPage = 1;
        $scope.pageChanged();
    }

    $scope.pageChanged = function () {
        $scope.offset = ($scope.currentPage - 1) * $scope.pageSize
        $scope.lastShown = Math.min($scope.offset + $scope.pageSize + 1, $scope.totalItems);
    };

    $scope.setOrder = function (orderBy) {
        if (orderBy === $scope.orderBy)
            $scope.orderBy = '-' + orderBy;  // Reverse the sort
        else
            $scope.orderBy = orderBy;
    }

    $scope.filterText = function (arr) {
        return filterFilter(arr, $scope.searchText);
    }

    /************************************************************************************************
     * Initialize
     */
    $scope.$watch('searchText', function (term) {
        $scope.applyFilter();
    });

});

app.directive('atomEntries', function ($window) {
    var config = {
        restrict: 'EA',
        scope: {
            entries: "=",
            orderBy: "@",
            remove: "&"
        },
        templateUrl: 'app/main/atomEntries.html',
        controller: 'AtomEntryController',
        link: function (scope, element, attrs) {
            // Bind this scope to its container in the DOM
            scope.node = element[0];

            // Determine whether to show or hide the remove button
            scope.showRemove = "remove" in attrs;

            // watch for the value to bind
            scope.$watch('entries', function (newValue, oldValue) {
                if (newValue)
                    scope.onModelLoaded(newValue);
            });
        }
    }

    return config;
});